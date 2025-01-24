from flask import Flask, request, render_template, jsonify, redirect, url_for, session, make_response
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, set_access_cookies, \
    unset_jwt_cookies

from shop_service import Store, create_database

app = Flask(__name__)
shop = Store()
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
    print(request.json)
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    print(username , password)
    if username == 'admin' and password == 'admin':
        access_token = create_access_token(identity=username)
        resp = make_response(redirect("/"))
        set_access_cookies(resp, access_token)
        return resp
    else:
        return 'Invalid username or password', 401
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
        group_id = request.args['group_id']
    except:
        group_id = None
    return shop.get_all_products(group_id)

@app.route('/', methods=['GET'])
@jwt_required()
def index():
    # get_jwt_identity()
    groups = shop.get_all_groups()
    try:
        group_id = request.args['group_id']
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
    product = shop.get_product(id)
    if product.get('description') is not None:
        product['description'] = product.get('description').split('\n')
    else:
        product['description'] = []
    print(product)
    return render_template('product.html',product=product)


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

if __name__ == '__main__':
    # create_database()
    app.run()
    shop.close()