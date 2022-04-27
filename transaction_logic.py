# Business logic is in this file; everything here is meant to be called in 
# flask_app.py in response to API calls

# Using a JSON data store because I already know how to work with that and
# Flask makes in-memory storage more difficult
from distutils.log import error
import json, os
from datetime import datetime

class transaction_logic:
    """
    This is a library class used to separate the project's business logic from
    its API code. flask_app.py will instantiate it for access to its methods
    when the app code is imported. It serves no purpose beyond this improved
    modularity. See method docstrings for explanations of individual features.
    """

    # convenience constants
    _datetime_format = "%Y-%m-%dT%H:%M:%SZ"
    _req_fields = ( "payer" , "points" , "timestamp" )

    def __init__(self, filename = None):
        """Loads into memory a transaction list from a JSON file with supplied
        name containing a 'transactions' property, or creates an empty
        transaction list if one is not supplied. I have not added any
        functionality elsewhere to persist changes to the transaction list
        as this is not required per the assignment, but I did create
        transactions.json to provide dummy transactions that would
        facilitate testing."""
        self.data = None

        if filename is None:
            self.data = {}
        else:
            with open(os.getcwd() + os.sep + filename, 'r') as f:
                self.data = json.load(f)["transactions"]

    def payer_balances(self):
        """This function returns a dict of all unique payers in self.data
        (the stored transaction list) along with their current point totals
        (which may be zero).
        Can be called either directly by the API or transaction_logic methods."""

        payers = set( ( t["payer"] for t in self.data ) )
        return { p : sum( ( t["points"] for t in self.data \
            if t["payer"] == p ) ) for p in payers }

    def add_points(self, transaction):
        """Adds a transaction to the stored list via a wrapped call to 
        ._new_transaction(). Since that method can perform either adds or
        spends, the input is checked and confirmed to be positive before
        passing it. All other required validation is performed during the call
        to ._new_transaction().
        
        Returns nothing."""
        try:
            assert transaction['points'] > 0
            self._new_transaction(transaction)
        except KeyError:
            raise ValueError("Field 'points' (int) is missing")
        except AssertionError:
            raise ValueError("Invalid value for field 'points', must be positive int")
        
    def _new_transaction(self, to_add):
        """
        This function takes a transaction as dict and adds it to the list of
        stored transactions iff it is well-formed. Input validation is
        separated into ._validate_transaction() for readability. Not meant to 
        be called from the API, only by other transaction_logic methods. The 
        negative transactions created when spending points are added by calls
        to this function.

        This function returns nothing but will raise an error (via the call to
        ._validate_transaction()) if a malformed transaction object is passed
        to it.
        """
        self._validate_transaction(to_add)
        # Input is valid if we've gotten this far
        self.data.append({ k:to_add[k] for k in transaction_logic._req_fields})

    def _validate_transaction(self, transaction):
        """
        Validates a single transaction object for use by ._new_transaction(). Separated
        from that function to reduce the frequency of write transactions. See error
        messages in the try block for how a transaction can be invalid. Assertions
        make the conditions easier to read and the use of the errormsg variable simplifies
        the exception handling. Not meant to be called directly; only ._new_transaction()
        should ever call this.
        """
        errormsg = None
        try:
            # Required data all present
            errormsg = "One of the required fields (payer, points, timestamp) is missing"
            assert all(x in transaction for x in transaction_logic._req_fields)
            # Correct types
            errormsg = "Type of field 'payer' is invalid, must be string"
            assert type(transaction["payer"]).__name__ == "str"
            errormsg = "Type of field 'timestamp' is invalid, must be string"
            assert type(transaction["timestamp"]).__name__ == "str"
            errormsg = "Type or value of field 'points' is invalid, must be nonzero int"
            assert type(transaction["points"]).__name__ == "int" and transaction["points"] != 0
            # Time format is correct and transaction does not take place in future
            errormsg = "Transaction timestamp is in the future"
            assert datetime.strptime(transaction["timestamp"], transaction_logic._datetime_format) \
                <= datetime.now()
            # Transaction won't take overall balance negative
            balances = self.payer_balances()
            errormsg = "Transaction exceeds total available point balance"
            assert transaction["points"] + sum(b for b in balances.values()) >= 0
            # Transaction won't take payer balance negative
            # Transaction doesn't try to spend from a first-time payer
            errormsg = "Transaction exceeds available points to spend for this payer"
            assert transaction["points"] + ( 0 if transaction["payer"] not in balances \
                else balances[transaction["payer"]] ) >= 0
        except AssertionError:
            # raised by most possible failures
            raise ValueError(errormsg)
        except TypeError:
            # raised if passed object is not a dict, when we try to check the types of fields
            raise ValueError("Each transaction object must be a dictionary containing keys 'payer' (str), 'points' (int) and 'timestamp' (str). Other keys will not cause problems but will be ignored")
        except ValueError:
            # raised if the timestamp format is incorrect when we try to parse it
            raise ValueError("Timestamp format incorrect, use YYYY-MM-DDTHH:MM:SSZ")

    def spend_points(self, amount):
        """
        This function takes a dict indicating an integer amount of points to
        spend and attempts to spend them.
        
        It will raise an error if the requested amount is strictly greater than
        the total available point balance across all payers. If the amount is 
        less than or equal to the available point balance, it will spend the 
        oldest previously-unspent points in the transaction list first until 
        the requested amount has been spent, never allowing any payer's balance
        to go negative.

        Transactions are split up by payer in order to identify the oldest
        available points for each payer, then merged and sorted again by age
        such that only available points are spent, in the order they were
        added, generating a dict indicating points spent by each payer
        with a positive balance at the time the transaction is requested.

        After determining how much to spend for each payer, ._new_transaction()
        is called with a dict for each payer whose points were spent indicating
        the amount they spent and the time the spend was requested.

        After all required transactions have been committed, a dict indicating
        the points spent by each payer is returned.
        """
        balances = self.payer_balances()
        # Input validation - verify possibility of spend across all payers
        errormsg = None
        try:
            errormsg = "Requested spend exceeds available point balance"
            assert amount <= sum( balances.values() )
            errormsg = "Must spend a positive number of points"
            assert amount > 0
        except AssertionError:
            raise ValueError( errormsg )
        # Spend according to rules

    # Which unspent points are oldest for each payer?
    # (have to separate by payer because transactions are by payer, and
    # without separating them a payer's balance might go negative )
        payers = [ k for k in balances.keys() if balances[k] > 0 ]
        print(payers)
        live_points = []

        for p in payers:
            print(p)
            history = sorted(
                [ t for t in self.data if t["payer"] == p ] ,
                key = lambda x: x["timestamp"]
            )
            debits = [ t for t in history if t["points"] < 0 ]
            credits = [ [t, t["points"]] for t in history if t["points"] > 0 ]
            
            i = None
            for d in debits:
                print(d)
                rem = abs(d["points"])
                if i is None:
                    i = 0
                while rem > 0:
                    diff = min(rem, credits[i][1])
                    credits[i][1] -= diff
                    rem -= diff
                    if credits[i][1] == 0:
                        i += 1
            
            live_points += credits[i:]

        # which unspent points are oldest overall? Have to sort by timestamp
        # again because separating by payer messed up our original order

        live_points = sorted(
            live_points ,
            key = lambda x: x[0]["timestamp"]
        )

        i = 0
        spends = {}
        for p in payers:
            spends[p] = 0
        while amount > 0:
            diff = min(amount, live_points[i][1])
            live_points[i][1] -= diff
            amount -= diff
            spends[live_points[i][0]["payer"]] -= diff
            if live_points[i][1] == 0:
                i += 1

        # now commit transactions based on what we're spending
        for k,v in spends.items():
            if v != 0:
                self._new_transaction(
                    {
                        "payer" : k,
                        "points": v ,
                        "timestamp": datetime.strftime(
                            datetime.now() ,
                            transaction_logic._datetime_format
                        )
                    }
                )
        
        return spends
            
db = transaction_logic( filename = "transactions.json")
            

