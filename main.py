from flask import Flask, render_template, request, redirect, url_for, session,flash,abort
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
from datetime import date
app = Flask(__name__)
app.config['SECRET_KEY'] = 'BigSecret21'
conn_str = "mysql://root:Treyjg2121@localhost/ecommerce"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

def t(str):
    alph = "abcdefghijklmnopqrstuvwxyz"
    sum = 0
    for char in str:
        sum += alph.find(char) + 1
    return sum

@app.route("/", methods=['GET','POST'])
def index():
    return render_template("index.html")

@app.route("/Login", methods=['GET','POST'])
def Login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        password = request.form['password']
        session['password'] = password
        account_type = request.form['account_type']
        session['account_type'] = account_type
        user_query = text("select * from accounts where username = :username AND password = :password AND account_type = :account_type" )
        params = {"username": username, "password": password, "account_type" :account_type}
        with engine.connect() as conn:
            user = conn.execute(user_query, params).fetchone()
        if user is None:
            return render_template('Login.html')
        if account_type == "Admin":
            return render_template('Admin_Vendor.html')
        if account_type == "Vendor":
            return render_template('Admin_Vendor.html')
        if account_type == "User":
            return render_template("Products.html")
    else:
        return render_template("Login.html")

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    try:
        session.pop('username', None)
        flash('You have successfully logged out.', 'success')
    except KeyError:
        flash('You were not logged in to begin with.', 'error')
    return redirect(url_for('Login'))
@app.route("/Registration", methods=['GET','POST'])
def Registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        account_type = request.form['account_type']
        query = text(
            "INSERT INTO accounts(username,password,email,account_type)"
            "VALUES(:username, :password, :email, :account_type)")
        params = {"username": username,"password":password,"email":email,"account_type":account_type}
        with engine.connect() as conn:
            conn.execute(query, params)
            conn.commit()
        return redirect(url_for('Login'))
    else:
        return render_template("Registration.html")

@app.route('/Products', methods=['GET', 'POST'])
def Products():
    query = text("SELECT * FROM products")
    with engine.connect() as conn:
        products = conn.execute(query).fetchall()
    return render_template('products.html', products=products)

@app.route('/add_to_cart', methods=['GET', 'POST'])
def add_to_cart():
    product_id = request.args.get('product_id')
    product_name = request.args.get('product_name')
    product_type = request.args.get('product_type')
    product_cost = request.args.get('product_cost')
    product_quality = request.args.get('product_quality')
    vendor_name = request.args.get('vendor_name')
    img_url = request.args.get('img_url')
    ordered_by = session['username']
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append({
        'product_id': product_id,
        'product_name': product_name,
        'product_type': product_type,
        'product_cost': product_cost,
        'product_quality': product_quality,
        'vendor_name': vendor_name,
        'img_url': img_url,
        'ordered_by': ordered_by
    })
    return "Added to cart"

@app.route('/cart', methods=['GET'])
def cart():
    if 'username' not in session:
        return redirect(url_for('Login'))
    if 'cart' not in session:
        session['cart'] = []
    cart_items = session['cart']
    cart_total = sum(item['product_cost'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, cart_total=cart_total)
@app.route('/Accounts', methods=['GET','POST'])
def Accounts():
    if 'username' in session:
        username = session['username']
        query = text("SELECT * FROM accounts WHERE username = :username")
        params = {'username': username}
        with engine.connect() as conn:
            accounts = conn.execute(query, params).fetchall()
        return render_template('Accounts.html', accounts=accounts)
    else:
        return redirect(url_for('Login'))

@app.route('/VendorAdd', methods=['GET', 'POST'])
def AddProducts():
    if request.method == 'POST':
        if session['account_type'] == "Admin":
            product_name = request.form['product_name']
            product_type = request.form['product_type']
            product_cost = request.form['product_cost']
            vendor_name = request.form['vendor_name']
            img_url = request.form['img_url']
            query = text("INSERT INTO products(product_name, product_type, product_cost, vendor_name, img_url) "
                         "VALUES(:product_name, :product_type, :product_cost, :vendor_name, :img_url)")
            params = {"product_name": product_name, "product_type": product_type, "product_cost": product_cost,
                      "vendor_name": vendor_name, "img_url": img_url}
            with engine.connect() as conn:
                conn.execute(query, params)
                conn.commit()
                return render_template("Products.html")
        elif session['account_type'] == "Vendor":
            return render_template("VendorAdd.html")
        else:
            return abort(403)
    else:
        if session['account_type'] == "Vendor" or session['account_type'] == "Admin":
            return render_template("VendorAdd.html")
        else:
            return abort(403)
@app.route('/Chat', methods=['GET', 'POST'])
def Chat():
    if request.method == 'POST':
        Your_User = request.form['Your_User']
        username = request.form['username']
        account_type = request.form['account_type']
        message = request.form['message']
        query = text(
            "INSERT INTO Chats(sender_username,username,account_type,message)"
            "VALUES(:sender_username, :username, :account_type, :message)")
        params = {"sender_username" :Your_User,"username": username, "account_type": account_type, "message": message}
        with engine.connect() as conn:
            conn.execute(query, params)
            conn.commit()
        return redirect(url_for('show_chats', username=username))
    else:
        return render_template("Chat.html")

@app.route('/Show', methods=['GET', 'POST'])
def show_chats():
    if request.method == 'POST':
        username = request.form['username']
        query = text("SELECT * FROM Chats WHERE username = :username")
        params = {'username': username}
        with engine.connect() as conn:
            chats = conn.execute(query, params).fetchall()
        return render_template('Chat.html', chats=chats, username=username)
    else:
        return render_template('Chat.html')

@app.route('/Review', methods = ['GET','POST'])
def Review():
    if request.method == 'Post':
        product_name = request.form['product_name']
        product_type = request.form['product_type']
        product_cost = request.form['product_cost']
        Vendor_name = request.form['Vendor_name']
        review = request.form['review']
        query = text(
            "INSERT INTO review(product_name,product_type,product_cost,Vendor_name,review)"
            "VALUES(:product_name, :product_type, :product_cost, :Vendor_name :review)")
        params = {"product_name" :product_name,"product_type": product_type, "product_cost": product_cost, "Vendor_name": Vendor_name, "review": review}
        with engine.connect() as conn:
            conn.execute(query, params).fetchall()
            conn.commit()
        return render_template('Review.html' )
    else:
        return render_template('Review.html')

@app.route("/Admin_Vendor", methods = ["GET","Post"])
def adminVendor():
    return render_template('Admin_Vendor.html')

@app.route('/Recieved', methods = ["GET","POST"])
def Recieved():
    return render_template('Recieved Orders.html')
if __name__ == '__main__':
    app.run(debug=True)