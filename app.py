# from flask import Flask, jsonify, request
# from flask_sqlalchemy import SQLAlchemy
# from flask_marshmallow import Marshmallow
# from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
# import os

# app = Flask(__name__)

# basedir = os.path.abspath(os.path.dirname(__file__))
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")
# db = SQLAlchemy(app)
# ma = Marshmallow(app)
# # app.config["JWT_SECRET_KEY"] = 'Wcw4xvlkDAYX-L5c' #cambia esto
# # jwt = JWTManager(app)

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String, unique=False)
#     email = db.Column(db.String, unique=True)
#     password = db.Column(db.String, unique=False)
#     def __init__(self, username, email, password):
#         self.username = username
#         self.email = email
#         self.password = password
# class UserSchema(ma.Schema):
#      username = ma.String()
#      email = ma.String()
#      password = ma.String()

# # class Admin(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     username = db.Column(db.String, unique=False)
# #     email = db.Column(db.String, unique=True)
# #     password = db.Column(db.String, unique=False)

# #     def __init__(self, username, email, password):
# #         self.username = username
# #         self.email = email
# #         self.password = password

# # class AdminSchema(ma.Schema):
# #     username = ma.String()
# #     email = ma.String()
# #     password = ma.String()


# user_schema = UserSchema()
# # users_schema= UserSchema(many=True)
# # admin_schema = AdminSchema()
# # admins_schema= AdminSchema(many=True)

# @app.route("/")
# def greeting():
#     return "Hello Itzala"

# # @app.route("/profile", methods=["GET"])
# # def getProfile():
# #     username = request.json.get(user_schema.username)
# #     return username
# users = [
#     {
#         "id": 1,
#         "username": "test",
#         "email": "test@test.eus"
#     },
#     {
#         "id": 2,
#         "username": "test-dos",
#         "email": "testdos@test.eus"
#     },
#     {
#         "id": 3,
#         "username": "test-tres",
#         "email": "testtres@test.eus"
#     }
# ]

# @app.route("/profile", methods=["POST", "GET"])
# def get_profiles():
#     user = User.query.get(User.username)
#     return user_schema.jsonify(user)

# # @app.route("/profile", methods=["POST"])
# # def createProfile():
# #     username = request.json(["username"])
# #     email = request.json(["email"])
# #     password = request.json(["password"])

# #     new_user = User(username, email, password)

# #     db.session.add(new_user)
# #     db.session.commit()

# #     user = User.query.get(new_user.id)
# #     return user_schema.jsonify(user)

# # @app.route("/login", methods=["POST"])
# # def login():
# #     username= request.json.get(admin_schema.username or user_schema.username, None)
# #     password= request.json.get(admin_schema.password or user_schema.password, None)
# #     if username != "test" or password != "test":
# #         return jsonify({"msg": "Bad username or password"}), 401

# #     access_token = create_access_token(identity=username)
# #     return jsonify(access_token=access_token)

# # @app.route("/protected", methods=["GET"])
# # @jwt_required()
# # def protected():
# #     current_user = get_jwt_identity()
# #     return jsonify(logged_in_as=current_user), 200


# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
app.config["JWT_SECRET_KEY"] = 'Wcw4xvlkDAYX-L5c'
app.config['JWT_VERIFY_SUB'] = False
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=False)
    email = db.Column(db.String(144), unique=True,)
    password = db.Column(db.String(144), unique=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class UserSchema(ma.Schema):
    id = ma.Integer()
    username = ma.String()
    email = ma.String()
    password = ma.String()


user_schema = UserSchema()
users_schema = UserSchema(many=True)

@app.route("/")
def greeting():
    return "Bienvenido al portal api de Itzala"


# Endpoint to create a new guide
@app.route('/user', methods=["POST"])
def add_users():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    new_user = User(username, email, password)

    db.session.add(new_user)
    db.session.commit()

    user = User.query.get(new_user.id)

    return user_schema.jsonify(user)

# Endpoint to log in with an existing user
@app.route("/login", methods=["POST"])
def login():
    password = request.json.get("password")
    email = request.json.get("email")

    user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()


    if user and user.password == password and user.email == email:
        access_token = create_access_token(identity={"email": email, "password": password})
        return jsonify(access_token=access_token)
    else:
        return jsonify({"msg": "Bad email or password"}), 401

    

# ruta a la carpeta: "C:\Users\Enara\OneDrive\Escritorio\itzala_back\segunda_prueba_pipenv"

# @app.route("/protected", methods=["GET"])
# @jwt_required()
# def protected():
#     current_user = get_jwt_identity()
#     return jsonify(logged_in_as=current_user), 200

# Endpoint to query all guides
@app.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    current_user = get_jwt_identity()
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result, current_user), 200, {'Access-Control-Allow-Origin':'*'}

@app.route("/user/<id>", methods=["GET"])
def get_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user), 200, {'Access-Control-Allow-Origin':'*'}

# Endpoint for updating a guide
@app.route("/user/<id>", methods=["PUT"])
def user_update(id):
    user = User.query.get(id)
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    user.username = username
    user.email = email
    user.password = password

    db.session.commit()
    return user_schema.jsonify(user)

# Endpoint for deleting a record
@app.route("/user/<id>", methods=["DELETE"])
def user_delete(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return user_schema.jsonify(user)

if __name__ == '__main__':
    app.run(debug=True)

# Para generar secret key en python rapl: 1. import os, os.urandom(12) 2. import secrets, secrets.token_urlsafe(12)