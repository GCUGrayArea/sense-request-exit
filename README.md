# sense-request-exit
A take-home coding assessment performed for an unspecified company. 

The assignment calls for an API with three endpoints: one to check current payer balances, one to add transactions for a specified payer and date, and one to spend points if they're available. The results have no persistence because the assignment doesn't call for any persistence, but a list of dummy transactions helpful for testing are loaded by default from `transactions.json`. The routes for this project are as follows:

| HTTP method | URI path  | Description                                                                                                                    | Request body                                                                                              | Response Body                                                                                      |
|-------------|-----------|--------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| GET         | /balances | Returns a list of payers in the stored transaction history and their current point balances.                                   | empty                                                                                                     | JSON object with payer (str) :  ( int ) for each payer with one or more transactions stored        |
| POST        | /add      | Adds a specified number of points associated with a specified payer to a specified time in the stored transaction history.     | JSON object with payer: (str), points: (int), timestamp: (datetime str of format “YYYY-MM-DDTHH:MM:SSZ” ) | empty                                                                                              |
| POST        | /spend    | Spends a specified number of points (if available), oldest first, without letting any payer’s balance go negative as a result. | JSON object with points: (int)                                                                            | JSON object with payer (str) : (int) for each payer whose points were spend fulfilling the request |

More detail for the API routes and the additional functions they call can be found in their respective docstrings.

Python's Flask web framework is used because it's the easiest way I know to make an API of this sort. A few other standard Python modules are used as needed. The API code is fully segregated from the business logic by the creation of the `transaction_logic` library class in `transaction_logic.py`, which is instantiated when the application runs and whose methods are called as needed.

This was fun to make, but took longer than I'd have liked due to the surprising complexity of spending the oldest points first regardless of payer.
