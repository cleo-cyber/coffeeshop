import os
from tkinter.font import BOLD
from turtle import title
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink,db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@DONEimplement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def get_drinks():
    drinks=Drink.query.all()
   
    if len(drinks)<=0:
            abort(404)
    return jsonify({
        'success':True,
        'drinks':[drink.short() for drink in drinks]
    })


'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    try:
        drinks = Drink.query.all()

        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        }), 200
    except:
        abort(404)

'''
@DONEimplement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    body=request.get_json()
    new_title=body.get('title',None)
    new_recipe=body.get('recipe',None)

    if new_title is None or new_recipe is None:
        abort(422)
    try:
        #check if recipe is a dictionary object
        if isinstance(new_recipe,dict):
            new_recipe=[new_recipe]
        new_drink=Drink(
            title=new_title,
            recipe=json.dumps(new_recipe)
        )

        new_drink.insert()
        return jsonify({
            'success':True,
            'drinks':[new_drink.long()]
        })

       
    except:
        # db.session.rollback()
        abort(422)
    finally:
        db.session.close()
 
     
'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def modify_drink(payload,drink_id):
    drink=Drink.query.filter(Drink.id==drink_id).one_or_none()
    if drink is None:
        abort(404)
    body=request.get_json()
    update_title=body.get('title')
    update_recipe=body.get('recipe')
    try:
        if update_title:
            drink.title=update_title
        if update_recipe:
            if isinstance(update_recipe,dict):
                update_recipe=[update_recipe]

                drink.recipe=json.dumps(update_recipe)
        drink.update()
        return jsonify({
                "success":True,
                "drinks":[drink.long()]
            })
    except:
        abort(404)

'''
@DONE implement endpoint
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
def delete_drink(jwt,drink_id):
    drink=Drink.query.filter(Drink.id==drink_id).one_or_none()
    if drink is None:
        abort(404)
    drink.delete()
    return jsonify({
        "success":True,
        "deleted":drink_id
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
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
#right one

'''

@DONE implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success':False,
        'error':404,
        'message':'Not Found'
    }),404

'''
@DONE implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success":False,
        'error':400,
        'message':'Bad Request'
    }),400