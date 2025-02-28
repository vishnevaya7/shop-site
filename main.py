from flask import Flask, request, render_template, jsonify, redirect, url_for, make_response
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, set_access_cookies, \
    unset_jwt_cookies

from shop_service import Store
from user_service import UserService

app = Flask(__name__)
shop = Store()
user_service = UserService()
app.config['SECRET_KEY'] = 'your-super-secret-key'
app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
jwt = JWTManager(app)
class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user = user_service.get_user(username, password)
    print('user = ', user)

    if user.get('id') is not None:
        access_token = create_access_token(identity=user.get('username'))
        resp = make_response(jsonify({"message": "Login successful"}), 200)
        resp.mimetype = 'application/json'
        set_access_cookies(resp, access_token)
        return resp
    else:
        return jsonify({"message": "Invalid username or password"}), 401
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/login', methods=['GET'])
def login_view():
    return render_template("login.html")
@app.route('/logout', methods=['GET'])
def logout():
    resp = make_response(redirect(url_for('login_view')))
    unset_jwt_cookies(resp)
    return resp

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        group_id = int(request.args['group_id'])
    except:
        group_id = None
    return shop.get_all_products(group_id)


@app.route('/basket', methods=['GET'])
@jwt_required()
def basket():
    groups = shop.get_all_groups()

    username = get_jwt_identity()
    products = shop.get_products_in_basket(username)
    print(products)
    sum_total_price = 0
    for product in products:
        total_price = product.get('price') * product.get('quantity')
        product['total_price'] = f"{total_price:,}"
        sum_total_price += total_price
    sum_total_price = f"{sum_total_price:,}"
    return render_template('basket.html',username=username, products=products,sum_total_price=sum_total_price,groups=groups)



@app.route('/basket', methods=['POST'])
@jwt_required()
def add_to_basket():
    username = get_jwt_identity()
    print(request.json)
    product_id = request.json.get('product_id', None)
    print(product_id)
    count = request.json.get('count', 1)
    print(count)
    shop.add_into_basket(username, product_id, count=count)
    return "OK"

@app.route('/api/basket/<id>', methods=['DELETE'])
@jwt_required()
def delete_product_from_basket(id):
    username = get_jwt_identity()
    shop.delete_product_from_basket(id,username)
    return "true"
@app.route('/', methods=['GET'])
@jwt_required()
def index():
    # get_jwt_identity()
    groups = shop.get_all_groups()
    try:
        group_id = int(request.args['group_id'])
    except:
        group_id = None
    print(group_id)
    return render_template('index.html',groups=groups,group_id=group_id)

@jwt.unauthorized_loader
def unauthorized_callback(callback):
    return redirect(url_for('login', next=request.url))

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    return redirect(url_for('login', next=request.url))

@app.route('/product/<id>', methods=['GET'])
def product(id):
    groups = shop.get_all_groups()
    product = shop.get_product(id)
    if product.get('description') is not None:
        product['description'] = product.get('description').split('\n')
    else:
        product['description'] = []
    print(product)
    return render_template('product.html',product=product,groups=groups)


@app.route('/api/products/<id>', methods=['DELETE'])
def delete_product(id):
    shop.delete_product(id)
    return "true"


@app.route('/api/products/<id>', methods=['GET'])
def get_product(id):
    return shop.get_product(id)



@app.route('/api/products', methods=['POST'])
def add_product():
    req = request.json
    shop.add_product(req['name'], req['price'], req['quantity'])
    return "true"

@app.route('/api/products/<id>', methods=['PATCH'])
def update_product(id):
    req = request.json
    shop.update_product(id, req.get('name',None), req.get('price',None), req.get('quantity',None))
    return "true"

@app.route('/api/order', methods=['GET'])
@jwt_required()
def get_order():
    username = get_jwt_identity()
    shop.get_order(username)
    return "true"





if __name__ == '__main__':
    # create_database()
    app.run(host="0.0.0.0", port=80, debug=True)
    shop.close()