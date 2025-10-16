from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt, get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
import os

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
app.config["JWT_SECRET_KEY"] = 'NAwmqQlzss3OCieT_6-SulHpkRI'
app.config['JWT_VERIFY_SUB'] = False
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours = 2)
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "None"

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)


# Gestión de usuarios
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(144), unique=True, nullable=False)
    password = db.Column(db.String(144), unique=False, nullable=False)

    def __init__(self, user, email, password):
        self.user = user
        self.email = email
        self.password = password


class UserSchema(ma.Schema):
    id = ma.Integer()
    user = ma.String()
    email = ma.String()


user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Gestión de administradores
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(144), unique=True, nullable=False)
    password = db.Column(db.String(144), unique=False, nullable=False)

    def __init__(self, user, email, password):
        self.user = user
        self.email = email
        self.password = password


class AdminSchema(ma.Schema):
    id = ma.Integer()
    user = ma.String()
    email = ma.Email()
    password = ma.String()


admin_schema = AdminSchema()
admins_schema = AdminSchema(many=True)

# Gestión de reservas
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), unique=False, nullable=False)
    quantity = db.Column(db.Integer, unique=False, nullable=False)
    comment = db.Column(db.String(150), unique=False, nullable=True)
    reservation_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref="reservation")

    def __init__(self, date, quantity, comment, reservation_user_id):
        self.date = date
        self.quantity = quantity
        self.comment = comment
        self.reservation_user_id = reservation_user_id

class ReservationSchema(ma.Schema):
    id = ma.Integer()
    reservation_user_id = ma.Integer()
    date = ma.String()
    quantity = ma.Integer()
    comment = ma.String()

reservation_schema = ReservationSchema()
reservations_schema = ReservationSchema(many=True)

# Gestión de productos (platos de la carta)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(200), unique=True, nullable=False)
    course = db.Column(db.Integer, unique=False, nullable=False)
    price = db.Column(db.Float, unique=False, nullable=False)

    def __init__(self, product, course, price):
        self.product = product
        self.course = course
        self.price = price

class ProductSchema(ma.Schema):
    id = ma.Integer()
    product = ma.String()
    course = ma.Integer()
    price = ma.Float()

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

#Gestión de pedidos
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.String(450), unique=False, nullable=False)
    order_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref="order")

    def __init__(self, order, order_user_id):
        self.order = order
        self.order_user_id = order_user_id

class OrderSchema(ma.Schema):
    id = ma.Integer()
    order = ma.String()
    order_user_id = ma.Integer()

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

#Endpoints:

# Inicio
@app.route("/")
def greeting():
    return "Bienvenido al portal api de Itzala"

# Endpoint para crear un nuevo usuario
@app.route('/user', methods=["POST"])
def add_users():
    user = request.json['user']
    email = request.json['email']
    password = request.json['password']

    if user == None or email == None or password == None:
        return jsonify({"msg": "Datos incorrectos"}), 400
    
    user_exist = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
    if user_exist:
        return jsonify({"msg": "Este email ya tiene una cuenta"}), 400

    new_user = User(user, email, password)

    db.session.add(new_user)
    db.session.commit()

    user = db.session.get(User, new_user.id)

    return user_schema.jsonify(user), 200

# Endpoint para crear una cuenta de administrador (no accesible en el frontend)
@app.route('/admin', methods=["POST"])
def add_admin():
    user = request.json['user']
    email = request.json['email']
    password = request.json['password']

    if user == None or email == None or password == None:
        return jsonify({"msg": "Datos incorrectos"}), 400

    new_admin = Admin(user, email, password)

    db.session.add(new_admin)
    db.session.commit()

    admin = db.session.get(Admin, new_admin.id)

    return admin_schema.jsonify(admin)
 
# Endpoint para iniciar sesión como usuario o como administrador
@app.route("/login", methods=["POST"])
@jwt_required(optional=True)
def login():
    password = request.json.get("password")
    email = request.json.get("email")

    user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
    admin = db.session.execute(db.select(Admin).filter_by(email=email)).scalar_one_or_none()

    if user and user.password == password and user.email == email:
        access_token_cookie = create_access_token(identity={"email": email, "password": password}, additional_claims={"isAdmin": False})
        response = jsonify(logged_in="LOGGED_IN", status="user", user_id=user.id)
        response.set_cookie("access_token_cookie", access_token_cookie, max_age=7200, samesite='None', secure=True)
        return response, 200
    elif admin and admin.password == password and admin.email == email:
        access_token_cookie = create_access_token(identity={"email": email, "password": password}, additional_claims={"isAdmin": True})
        response = jsonify(logged_in="LOGGED_IN", status="admin")
        response.set_cookie("access_token_cookie", access_token_cookie, max_age=7200, samesite='None', secure=True)
        return response,  200
    else:
        return jsonify({"msg": "Contraseña o email incorrecto"}), 401

# Endpoint para cerrar sesión
@app.route("/logout", methods=["POST"])
@jwt_required()
def logout() :
    resp = jsonify(logged_in="NO_LOGGED_IN")
    resp.delete_cookie("access_token_cookie", samesite='None', secure=True)
    return resp, 200

# Endpoint para verificar que existe una sesión e identificar a quién pertenece
@app.route("/verify", methods=["GET"])
@jwt_required(optional=True)
def verify_user():
    identity = get_jwt_identity()
    if identity:
        email = identity["email"]
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        isAdmin = get_jwt()["isAdmin"]
        if isAdmin == True:
            return jsonify(status="admin", logged_in="LOGGED_IN")
        elif isAdmin == False:
            return jsonify(status="user", user_id=user.id, logged_in="LOGGED_IN")
        else:
            return jsonify(logged_in="NO_LOGGED_IN")
    else:
        return jsonify(logged_in="NO_LOGGED_IN")

# Endpoint para obtener todos los usuarios (solo para administrador)
@app.route("/users", methods=["GET"])
@jwt_required()
def get_users():
        is_admin = get_jwt()
        if is_admin["isAdmin"] == True:
            all_users = User.query.all()
            result = users_schema.dump(all_users)
            return jsonify(result=result), 200
        else:
            return "Not admin"

# Endpoint para obtener un usuario concreto (para perfil de usuario)
@app.route("/user/<id>", methods=["GET"])
@jwt_required()
def get_user(id):
    is_admin = get_jwt()
    if is_admin["isAdmin"] == False:
        user = db.session.get(User, id)
        return user_schema.jsonify(user), 200
    else:
        return "Not a logged in user"

# Endpoint para actualizar los datos de un usuario (en desuso, para futuros cambios)
@app.route("/user/<id>", methods=["PUT"])
@jwt_required()
def user_update(id):
    this_user = db.session.get(User, id)
    user = request.json['user']
    email = request.json['email']
    password = request.json['password']

    this_user.user = user
    this_user.email = email
    this_user.password = password

    db.session.commit()
    return user_schema.jsonify(this_user), 200

# Endpoint para eliminar un usuario (en desuso, para futuros cambios)
@app.route("/user/<id>", methods=["DELETE"])
@jwt_required()
def user_delete(id):
    user = db.session.get(User, id)
    db.session.delete(user)
    db.session.commit()

    return user_schema.jsonify(user)

# Endpoint para eliminar un plato del menú
@app.route("/menu-item", methods=["POST"])
@jwt_required()
def add_item():
    product = request.json["product"]
    course = request.json["course"]
    price = request.json["price"]

    new_product = Product(product, course, price)

    db.session.add(new_product)
    db.session.commit()

    prod = db.session.get(Product, new_product.id)

    return product_schema.jsonify(prod), 200

# Endpoint para obtener todos los platos del menú
@app.route("/menu-item", methods=["GET"])
def get_all_menu_items():
    all_items = Product.query.all()
    result = products_schema.dump(all_items)
    return jsonify(result)

# Endpoint para obtener un plato específico del menú
@app.route("/menu-item/<id>", methods=["GET"])
@jwt_required()
def get_menu_item(id):
    is_admin = get_jwt()
    if is_admin["isAdmin"]:
        menu_item = db.session.get(Product, id)
        return product_schema.jsonify(menu_item), 200
    else:
        return "Not a logged in user"

# Endpoint para eliminar un plato del menú
@app.route("/menu-item/<id>", methods=["DELETE"])
@jwt_required()
def product_delete(id):
    is_admin = get_jwt()
    if is_admin["isAdmin"] == True:
        product = db.session.get(Product, id)
        db.session.delete(product)
        db.session.commit()
        response = product_schema.jsonify(product)
        return response, 200
    else:
        return "You are not an admin"

# Endpoint para actualizar un plato del menú    
@app.route("/menu-item/<id>", methods=["PATCH"])
@jwt_required()
def item_update(id):
    is_admin = get_jwt()
    if is_admin["isAdmin"] == True:
        item = db.session.get(Product, id)
        product = request.json['product']
        price = request.json['price']
        course = request.json['course']

    item.product = product
    item.price = price
    item.course = course

    db.session.commit()
    return product_schema.jsonify(item), 200

# Endpoint para obtener todas las reservas
@app.route("/reservation", methods=["GET"])
@jwt_required()
def get_reservations():
    all_items = Reservation.query.all()
    result = reservations_schema.dump(all_items)
    return jsonify(result)

# Endpoint para obtener las reservas de un usuario
@app.route("/reservation/<id>", methods=["GET"])
@jwt_required()
def get_users_reservations(id):
    users_reservations = Reservation.query.filter_by(reservation_user_id=id)
    result = reservations_schema.dump(users_reservations)
    return jsonify(result), 200

# Endpoint para realizar una reserva
@app.route("/reservation", methods=["POST"])
@jwt_required()
def reserve():
    day = request.json["day"]
    quantity = request.json["quantity"]
    comment = request.json["comment"]
    user = request.json["user"]
    if day == None or quantity == None:
        return jsonify({"msg": "Datos incorrectos"}), 400   

    new_reservation = Reservation(day, quantity, comment, user)

    db.session.add(new_reservation)
    db.session.commit()

    res = db.session.get(Reservation, new_reservation.id)

    return reservation_schema.jsonify(res), 200

# Endpoint para realizar un pedido
@app.route("/order", methods=["POST"])
@jwt_required()
def make_order():
    order = request.json["order"]
    user = request.json["user"]

    new_order = Order(order, user)

    db.session.add(new_order)
    db.session.commit()

    res = db.session.get(Order, new_order.id)

    return order_schema.jsonify(res), 200

# Endpoint para obtener todos los pedidos
@app.route("/orders", methods=["GET"])
@jwt_required()
def get_all_orders():
    all_items = Order.query.all()
    result = orders_schema.dump(all_items)
    return jsonify(result), 200


# Endpoint para obtener los pedidos de un usuario
@app.route("/order/<id>", methods=["GET"])
@jwt_required()
def get_orders(id):
    users_orders = Order.query.filter_by(order_user_id=id)
    result = orders_schema.dump(users_orders)
    return jsonify(result), 200

    

if __name__ == '__main__':
    app.run(debug=True)