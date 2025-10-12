from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from flask_jwt_extended import get_jwt, get_jwt_identity, get_csrf_token
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
# app.config["JWT_CSRF_IN_COOKIES"] = True
# app.config["JWT_ACCESS_CSRF_COOKIE_NAME"] = "access_token_cookie"

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)


# Gestión de usuarios
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100), unique=False)
    email = db.Column(db.String(144), unique=True,)
    contraseña = db.Column(db.String(144), unique=False)

    def __init__(self, usuario, email, contraseña):
        self.usuario = usuario
        self.email = email
        self.contraseña = contraseña


class UsuarioSchema(ma.Schema):
    id = ma.Integer()
    usuario = ma.String()
    email = ma.String()
    # contraseña = ma.String()


usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)

# Gestión de administradores
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100), unique=False)
    email = db.Column(db.String(144), unique=True,)
    contraseña = db.Column(db.String(144), unique=False)

    def __init__(self, usuario, email, contraseña):
        self.usuario = usuario
        self.email = email
        self.contraseña = contraseña


class AdminSchema(ma.Schema):
    id = ma.Integer()
    usuario = ma.String()
    email = ma.Email()
    contraseña = ma.String()


admin_schema = AdminSchema()
admins_schema = AdminSchema(many=True)

# Gestión de reservas
class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    día = db.Column(db.String(10), unique=False, nullable=False)
    cantidad = db.Column(db.Integer, unique=False, nullable=False)
    comentario = db.Column(db.String(150), unique=False, nullable=True)
    reserva_usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    usuario = db.relationship("Usuario", backref="reserva")

    def __init__(self, día, cantidad, comentario, reserva_usuario_id):
        self.día = día
        self.cantidad = cantidad
        self.comentario = comentario
        self.reserva_usuario_id = reserva_usuario_id

class ReservaSchema(ma.Schema):
    id = ma.Integer()
    reserva_usuario_id = ma.Integer()
    día = ma.String()
    cantidad = ma.Integer()
    comentario = ma.String()

reserva_schema = ReservaSchema()
reservas_schema = ReservaSchema(many=True)

# Gestión de productos (platos de la carta)
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto = db.Column(db.String(200), unique=True, nullable=False)
    tiempo = db.Column(db.Integer, unique=False, nullable=False)
    precio = db.Column(db.Float, unique=False, nullable=False)

    def __init__(self, producto, tiempo, precio):
        self.producto = producto
        self.tiempo = tiempo
        self.precio = precio

class ProductoSchema(ma.Schema):
    id = ma.Integer()
    producto = ma.String()
    tiempo = ma.Integer()
    precio = ma.Float()

producto_schema = ProductoSchema()
productos_schema = ProductoSchema(many=True)

#Gestión de pedidos
class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido = db.Column(db.String(450), unique=False, nullable=False)
    pedido_usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    usuario = db.relationship("Usuario", backref="pedido")

    def __init__(self, pedido, pedido_usuario_id):
        self.pedido = pedido
        self.pedido_usuario_id = pedido_usuario_id

class PedidoSchema(ma.Schema):
    id = ma.Integer()
    pedido = ma.String()
    pedido_usuario_id = ma.Integer()

pedido_schema = PedidoSchema()
pedidos_schema = PedidoSchema(many=True)

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

    new_user = Usuario(user, email, password)

    db.session.add(new_user)
    db.session.commit()

    user = db.session.get(Usuario, new_user.id)

    return usuario_schema.jsonify(user)

# Endpoint para crear una cuenta de administrador (no accesible en el frontend)
@app.route('/admin', methods=["POST"])
def add_admin():
    usuario = request.json['usuario']
    email = request.json['email']
    contraseña = request.json['contraseña']

    nuevo_admin = Admin(usuario, email, contraseña)

    db.session.add(nuevo_admin)
    db.session.commit()

    admin = db.session.get(Admin, nuevo_admin.id)

    return admin_schema.jsonify(admin)
 
# Endpoint para iniciar sesión como usuario o como administrador
@app.route("/login", methods=["POST"])
@jwt_required(optional=True)
def login():
    contraseña = request.json.get("password")
    email = request.json.get("email")

    usuario = db.session.execute(db.select(Usuario).filter_by(email=email)).scalar_one_or_none()
    admin = db.session.execute(db.select(Admin).filter_by(email=email)).scalar_one_or_none()

    if usuario and usuario.contraseña == contraseña and usuario.email == email:
        access_token_cookie = create_access_token(identity={"email": email, "contraseña": contraseña}, additional_claims={"isAdmin": False})
        response = jsonify(logged_in="LOGGED_IN", status="usuario", usuario_id=usuario.id)
        response.set_cookie("access_token_cookie", access_token_cookie, max_age=7200)
        return response, 200
    elif admin and admin.contraseña == contraseña and admin.email == email:
        access_token_cookie = create_access_token(identity={"email": email, "contraseña": contraseña}, additional_claims={"isAdmin": True})
        response = jsonify(logged_in="LOGGED_IN", status="admin")
        response.set_cookie("access_token_cookie", access_token_cookie, max_age=7200)
        return response,  200
    else:
        return jsonify({"msg": "Contraseña o email incorrecto"}), 401

# Endpoint para cerrar sesión
@app.route("/logout", methods=["POST"])
@jwt_required()
def logout() :
    resp = jsonify(logged_in="NO_LOGGED_IN")
    unset_jwt_cookies(resp)
    return resp, 200

# Endpoint para verificar que existe una sesión e identificar a quién pertenece
@app.route("/verify", methods=["GET"])
@jwt_required(optional=True)
def verify_user():
    identity = get_jwt_identity()
    if identity:
        email = identity["email"]
        usuario = db.session.execute(db.select(Usuario).filter_by(email=email)).scalar_one_or_none()
        isAdmin = get_jwt()["isAdmin"]
        if isAdmin == True:
            return jsonify(status="admin", logged_in="LOGGED_IN")
        elif isAdmin == False:
            return jsonify(status="usuario", usuario_id=usuario.id, logged_in="LOGGED_IN")
        else:
            return jsonify(logged_in="NO_LOGGED_IN")
    else:
        return jsonify(logged_in="NO_LOGGED_IN")

# Endpoint para obtener todos los usuarios (solo para administrador)
@app.route("/usuarios", methods=["GET"])
@jwt_required()
def get_users():
        is_admin = get_jwt()
        if is_admin["isAdmin"] == True:
            all_users = Usuario.query.all()
            result = usuarios_schema.dump(all_users)
            return jsonify(result=result), 200
        else:
            return "Not admin"

# Endpoint para obtener un usuario concreto (para perfil de usuario)
@app.route("/usuario/<id>", methods=["GET"])
@jwt_required()
def get_user(id):
    is_admin = get_jwt()
    if is_admin["isAdmin"] == False:
        usuario = db.session.get(Usuario, id)
        return usuario_schema.jsonify(usuario), 200
    else:
        return "Not a logged in user"

# Endpoint para actualizar los datos de un usuario (en desuso, para futuros cambios)
@app.route("/usuario/<id>", methods=["PUT"])
@jwt_required()
def user_update(id):
    user = db.session.get(Usuario, id)
    usuario = request.json['usuario']
    email = request.json['email']
    contraseña = request.json['contraseña']

    user.usuario = usuario
    user.email = email
    user.contraseña = contraseña

    db.session.commit()
    return usuario_schema.jsonify(user), 200

# Endpoint para eliminar un usuario (en desuso, para futuros cambios)
@app.route("/usuario/<id>", methods=["DELETE"])
@jwt_required()
def user_delete(id):
    usuario = db.session.get(Usuario, id)
    db.session.delete(usuario)
    db.session.commit()

    return usuario_schema.jsonify(usuario)

# Endpoint para eliminar un plato del menú
@app.route("/menu-item", methods=["POST"])
@jwt_required()
def add_item():
    producto = request.json["producto"]
    tiempo = request.json["tiempo"]
    precio = request.json["precio"]

    nuevo_producto = Producto(producto, tiempo, precio)

    db.session.add(nuevo_producto)
    db.session.commit()

    prod = db.session.get(Producto, nuevo_producto.id)

    return producto_schema.jsonify(prod), 200

# Endpoint para obtener todos los platos del menú
@app.route("/menu-item", methods=["GET"])
def show_item():
    all_items = Producto.query.all()
    result = productos_schema.dump(all_items)
    return jsonify(result)

# Endpoint para obtener un plato específico del menú
@app.route("/menu-item/<id>", methods=["GET"])
@jwt_required()
def get_menu_item(id):
    is_admin = get_jwt()
    if is_admin["isAdmin"]:
        menu_item = db.session.get(Producto, id)
        return producto_schema.jsonify(menu_item), 200
    else:
        return "Not a logged in user"

# Endpoint para eliminar un plato del menú
@app.route("/menu-item/<id>", methods=["DELETE"])
@jwt_required()
def producto_delete(id):
    is_admin = get_jwt()
    if is_admin["isAdmin"] == True:
        producto = db.session.get(Producto, id)
        db.session.delete(producto)
        db.session.commit()
        response = producto_schema.jsonify(producto)
        return response, 200
    else:
        return "You are not an admin"

# Endpoint para actualizar un plato del menú    
@app.route("/menu-item/<id>", methods=["PATCH"])
@jwt_required()
def item_update(id):
    is_admin = get_jwt()
    if is_admin["isAdmin"] == True:
        item = db.session.get(Producto, id)
        producto = request.json['producto']
        precio = request.json['precio']
        tiempo = request.json['tiempo']

    item.producto = producto
    item.precio = precio
    item.tiempo = tiempo

    db.session.commit()
    return producto_schema.jsonify(item), 200

# Endpoint para obtener todas las reservas
@app.route("/reservation", methods=["GET"])
def get_reservations():
    all_items = Reserva.query.all()
    result = reservas_schema.dump(all_items)
    return jsonify(result)

# Endpoint para obtener las reservas de un usuario
@app.route("/reservation/<id>", methods=["GET"])
def get_reservation(id):
    users_reservations = Reserva.query.filter_by(reserva_usuario_id=id)
    result = reservas_schema.dump(users_reservations)
    return jsonify(result), 200

# Endpoint para realizar una reserva
@app.route("/reserva", methods=["POST"])
@jwt_required()
def reservar():
    day = request.json["day"]
    cantidad = request.json["cantidad"]
    comentario = request.json["comentario"]
    user = request.json["user"]

    nueva_reserva = Reserva(day, cantidad, comentario, user)

    db.session.add(nueva_reserva)
    db.session.commit()

    res = db.session.get(Reserva, nueva_reserva.id)

    return reserva_schema.jsonify(res), 200

# Endpoint para realizar un pedido
@app.route("/order", methods=["POST"])
def make_order():
    order = request.json["order"]
    user = request.json["user"]

    new_order = Pedido(order, user)

    db.session.add(new_order)
    db.session.commit()

    res = db.session.get(Pedido, new_order.id)

    return pedido_schema.jsonify(res), 200

# Endpoint para obtener los pedidos de un usuario
@app.route("/pedido/<id>", methods=["GET"])
def get_pedidos(id):
    users_pedidos = Pedido.query.filter_by(pedido_usuario_id=id)
    result = pedidos_schema.dump(users_pedidos)
    return jsonify(result), 200

    

if __name__ == '__main__':
    app.run(debug=True)

# Para generar secret key en python rapl: 1. import os, os.urandom(12) 2. import secrets, secrets.token_urlsafe(12)