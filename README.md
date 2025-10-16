# Itzala API
This app creates the database to manage data from Itzala frontend app and provides the routes to control the data coming from and going to the frontend.

## Database tables:
- User: manages the user profile data
    - id (primary key)
    - user
    - email
    - password

- Admin: manages the user profile data
    - id (primary key)
    - user
    - email
    - password

- Reservation: manages reservarions made by users
    - id (primary key)
    - date
    - quantity
    - comment
    - reservation_user_id (foreign key to user)

- Product: manages the menu-items
    - id (primary key)
    - product
    - course
    - price

- Order: manages food orders placed by users
    - id (primary key)
    - order
    - order_user_id (foreign key to user)

## API routes

### Greeting
```
@app.route("/")
def greeting():
```
### Create a user account
```
@app.route('/user', methods=["POST"])
def add_users():
```
It takes the following data: user, email and password. Returns created user's data.

### Create an admin account
```
@app.route('/admin', methods=["POST"])
def add_admin():
```
It takes the following data: user, email and password. Returns created admin's data.

### Log into a session (admin or user)
```
@app.route("/login", methods=["POST"])
@jwt_required(optional=True)
def login():
```
It takes the following data: email and password. Creates a JWT token and sets a cookie with it. It returns `logged_in="LOGGED_IN", status="user", user_id=user.id` if it is a user, and `logged_in="LOGGED_IN", status="admin"` if it is an admin. In case of error, returns `"msg": "Contraseña o email incorrecto"`

### Log out of a session (admin or user)
```
@app.route("/logout", methods=["POST"])
@jwt_required()
def logout() :
```
Deletes the cookie and returns a response with `logged_in="NO_LOGGED_IN"`.

### Verify a user or an admin
```
@app.route("/verify", methods=["GET"])
@jwt_required(optional=True)
def verify_user():
```
Verifys the JWT token and returns the same content as the login function if there is a valid JWT. If there is no valid token, it retuns `logged_in="NO_LOGGED_IN"`.

### Get all users
```
@app.route("/users", methods=["GET"])
@jwt_required()
def get_users():
```
If it is an admin user, it returns all users information. If it is not an admin, it return "Not admin".

### Get specific user
```
@app.route("/user/<id>", methods=["GET"])
@jwt_required()
def get_user(id):
```
The url takes the id. It returns the user information of the logged in user. If there is not a logged in user, it return "Not a logged in user".

### Update a user
```
@app.route("/user/<id>", methods=["PUT"])
@jwt_required()
def user_update(id):
```
The url takes the id. It takes updated user, email and password data and returns the updated user's data.

### Delete a user
```
@app.route("/user/<id>", methods=["DELETE"])
@jwt_required()
def user_delete(id):
```
The url takes the id. It deletes the user and returs it's information.

### Create a menu item
```
@app.route("/menu-item", methods=["POST"])
@jwt_required()
def add_item():
```
It takes product, course and price and returns the created products information.

### Get all menu items
```
@app.route("/menu-item", methods=["GET"])
def get_all_menu_items():
```
It returns all the menu items.

### Get specific menu item
```
@app.route("/menu-item/<id>", methods=["GET"])
@jwt_required()
def get_menu_item(id):
```
It returns the product related to the given id via url.

### Delete a menu item
```
@app.route("/menu-item/<id>", methods=["DELETE"])
@jwt_required()
def product_delete(id):
```
It deletes de item realted to the id given on the url. It returns the deleted product info.

### Update a menu item
```
@app.route("/menu-item/<id>", methods=["PATCH"])
@jwt_required()
def item_update(id):
```
It identifys the item via id on the url. It takes the updated product, course and price and returns the updated product info.

### Get all reservations
```
@app.route("/reservation", methods=["GET"])
def get_reservations():
```
It returns all the reservations

### Get a specific reservation
```
@app.route("/reservation/<id>", methods=["GET"])
def get_users_reservations(id):
```
It returns the reservation related to an specific id.

### Make a reservation
```
@app.route("/reservation", methods=["POST"])
@jwt_required()
def reserve():
```
It takes day, quantity and comment (optional) and returns the reservation info.

### Place an order
```
@app.route("/order", methods=["POST"])
@jwt_required()
def make_order():
```
It takes order and returns the orders info.

### Get all orders
```
@app.route("/orders", methods=["GET"])
@jwt_required()
def get_all_orders():
```
It returns all the orders.

### Get specific orders
```
@app.route("/order/<id>", methods=["GET"])
@jwt_required()
def get_orders(id):
```
It returns the orders related to an id given by the url.