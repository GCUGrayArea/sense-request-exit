from flask import Flask, Response, request
from transaction_logic import transaction_logic, db
import json

"""
This file contains the application and API code used to run the web service for
this assignment. It can be run from the command line:

    python3 flask_app.py

Nothing else is required. The Flask framework handles all requests. Flask's 
decorators (beginning with @ above the function definitions) indicate the
API endpoints and the request methods they allow. This file covers only the
API; see transaction_logic.py for business logic.
"""

# Instantiates a flask app, does nothing else
def create_app():
    app = Flask(__name__)
    return app

# instantiates this class so Flask endpoints can access its methods
app = create_app()

# Add transactions for a specific payer and date
@app.route("/add", methods = ['POST'] )
def add():
    """
    POST only - this modifies the stored transaction list in a non-idempotent
    way.

    This endpoint takes a transaction as a JSON object and attempts to add
    it to the stored transaction list.
    
    Valid input has properties 'points' (int), 'payer' (str) and 'timestamp'
    (str). Other fields will not cause problems but will be ignored.
    
    Input validation is performed by the transaction_logic object rather than
    here. Response code is 400 (with details in response body) if any input
    validation fails, and 200 with empty body if everything succeeds.
    """

    try:
        data = request.get_json( force = True )
        db.add_points(data)
        return Response(
            json.dumps({}) ,
            status = 200 ,
            mimetype='application/json' ,
        )
    except ValueError as e:
        return Response(
                    json.dumps({ "error": str(e) }) ,
                    status = 400 ,
                    mimetype='application/json' ,
        )

# Return all payer point balances
@app.route("/balances", methods = ['GET'])
def balances():
    """
    GET only - this returns stored information but cannot modify it

    This endpoint returns a JSON object with a property for the name of each payer in the current transaction
    list and their current point totals as ints.

    Any request body is ignored.
    
    Response code is 200 unless the attempt to access the transaction list
    fails somehow, and 500 in that case.
    """
    try:
        return Response(
            json.dumps(db.payer_balances()) ,
            status = 200 ,
            mimetype='application/json'
        )
    except Exception:
        # Hard to imagine when this would ever be needed, but *something* has
        # to be returned
        return Response(
            { "error": "Something went wrong" } ,
            status = 500 ,
            mimetype='application/json'
        )

@app.route("/spend", methods = ['POST'])
def spend():
    """
    POST only - this modifies the stored transaction list in a non-idempotent
    way.

    This endpoint takes a JSON object with a 'points' property and attempts
    to spend the request number of points. If the spend does not exceed
    available balance, it will return a JSON object with a property for the
    name of each payer with points available to spend and the number of their
    points spent.
    
    Valid input has property 'points' (int). Other fields will not cause
    problems but will be ignored.

    Response code is 200 with the JSON object indicating points spent if the
    operation succeeded, and 400 with an error message otherwise.
    """
    try:
        amount = request.get_json( force = True )
        return Response(
            json.dumps(db.spend_points(amount["points"])) ,
            status = 200 ,
            mimetype='application/json'
        )
    except ValueError as e:
        return Response(
            json.dumps({ "error" : str(e) }) ,
            status = 400 ,
            mimetype='application/json'
        )


if __name__ != 'main':
    # Allows the running of the app from the command line
    app.run(host="localhost", port=3000, debug=True)
