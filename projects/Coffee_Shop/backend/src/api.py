import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
with app.app_context():
    db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])

def get_drinks():
    # Query the database for all drinks
    drinks = Drink.query.all()

    # If no drinks are found, return a 404 error
    if len(drinks) == 0:
        abort(404)

    # Return the list of drinks in JSON format
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        # Check if the user has the required permission
        if 'get:drinks-detail' not in jwt['permissions']:
            abort(403)

        # Query the database for all drinks
        drinks = Drink.query.all()

        # If no drinks are found, return a 404 error
        if len(drinks) == 0:
            abort(404)

        # Return the list of drinks in JSON format
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        })
    except Exception as e:
        print(e)
        abort(422)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    # Check if the user has the required permission
    if 'post:drinks' not in jwt['permissions']:
        abort(403)

    # Get the request data
    body = request.get_json()
    print("BODY:", body)

    # Check if the required fields are present in the request data
    if 'title' not in body or 'recipe' not in body:
        abort(422)

    # Create a new drink instance
    new_drink = Drink(title=body['title'], recipe=json.dumps(body['recipe']))

    try:
        # Add the new drink to the database
        new_drink.insert()
    except Exception as e:
        print(e)

        abort(422)

    # Return the newly created drink in JSON format
    return jsonify({
        'success': True,
        'drinks': [new_drink.long()]
    })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, drink_id):
    # Check if the user has the required permission
    if 'patch:drinks' not in jwt['permissions']:
        abort(403)

    # Get the request data
    body = request.get_json()

    # Check if the required fields are present in the request data
    if 'title' not in body and 'recipe' not in body:
        abort(422)

    # Query the database for the drink with the given id
    drink = Drink.query.get(drink_id)

    # If the drink is not found, return a 404 error
    if drink is None:
        abort(404)

    # Update the drink's attributes based on the request data
    if 'title' in body:
        drink.title = body['title']
    if 'recipe' in body:
        drink.recipe = json.dumps(body['recipe'])

    try:
        # Update the drink in the database
        drink.update()
    except Exception as e:
        print(e)
        abort(422)

    # Return the updated drink in JSON format
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    # Check if the user has the required permission
    if 'delete:drinks' not in jwt['permissions']:
        abort(403)

    # Query the database for the drink with the given id
    drink = Drink.query.get(drink_id)

    # If the drink is not found, return a 404 error
    if drink is None:
        abort(404)

    try:
        # Delete the drink from the database
        drink.delete()
    except Exception as e:
        print(e)
        abort(422)

    # Return the id of the deleted drink in JSON format
    return jsonify({
        'success': True,
        'delete': drink_id
    })

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(ex):
    return jsonify({
        "success": False,
        "error": ex.status_code,
        "message": ex.error['description']
    }), ex.status_code


if __name__ == "__main__":
    app.debug = True
    app.run()
