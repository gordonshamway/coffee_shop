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
'''
db_drop_and_create_all()

## ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():
    '''
    @TODO implement endpoint
        GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    try:
        drinks = Drink.query.order_by(Drink.id).all()
    except Exception:
        abort(500)
    if not drinks:
        abort(404)
    else:
        return jsonify({
            "success": True,
            "drinks": [d.short() for d in drinks]
            })

@app.route('/drinks-detail', methods=['GET'])
#@requires_auth()
def get_drinks_detail():
    '''
    @TODO implement endpoint
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    try:
        drinks = Drink.query.order_by(Drink.id).all()
    except Exception:
        abort(500)
    if not drinks:
        abort(404)
    else:
        return jsonify({
            "success": True,
            "drinks": [d.long() for d in drinks]
            })


@app.route('/drinks', methods=['POST'])
#@requires_auth()
def post_new_drink():
    '''
    @TODO implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    '''
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    if None in [title, recipe]:
        abort(422)
    else:
        try:
            new_drink = Drink(title, recipe)
            new_drink.insert()
            
            return jsonify({
                    "success": True,
                    "drinks": [new_drink.long()]
                    })
        except Exception:
            abort(422)  


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
#@requires_auth()
def update_drink(drink_id):
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
    this_drink = Drink.query.filter_by(id=drink_id).first()
    if not this_drink:
        abort(404)
    else:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)
        if title == None and recipe == None:
            abort(422)
        else:
            this_drink.title = title
            this_drink.recipe = recipe
            try:
                this_drink.update()
                return jsonify({
                    "success": True,
                    "drinks": [this_drink.long()]
                    })
            except Exception:
                abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
#@requires_auth()
def delete_drink(drink_id):
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
    this_drink = Drink.query.filter_by(id=drink_id).first()
    this_drinks_id = this_drink.id
    if not this_drink:
        abort(404)
    else:
        try:
            this_drink.delete()
            return jsonify({
                        "success": True,
                        "delete": this_drinks_id
                        })
        except Exception:
            abort(422)

##########################
##### Error Handling #####
##########################
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "not found"
                    }), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "unauthorized"
                    }), 401

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

@app.errorhandler(500)
def server_error(error):
    return jsonify({
                    "success": False, 
                    "error": 500,
                    "message": "server error"
                    }), 500