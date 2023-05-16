# Import necessary modules
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
from datetime import date

# Create Flask app and set secret key
app = Flask(__name__)
app.config['SECRET_KEY'] = 'BigSecret21'

# Create database connection
conn_str = "mysql://root:Treyjg2121@localhost/ecommerce"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


def t(str):
    alph = "abcdefghijklmnopqrstuvwxyz"
    sum = 0
    for char in str:
        sum += alph.find(char) + 1
    return sum


# Define routes
@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@app.route("/Login", methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        account_type = request.form['account_type']
        # Query database for user account
        user_query = text(
            "select * from accounts where username = :username AND password = :password AND account_type = :account_type")
        params = {"username": username, "password": password, "account_type": account_type}
        result = conn.execute(user_query, params)
        user = result.fetchone()
        # Determine user account type and render appropriate template
        if user is None:
            return render_template('Login.html')
        else:
            session['id']= user[0]
            session['username'] = user[1]
            session['password'] = user[2]
            session['email'] = user[3]
            session['account_type'] = user[4]
            if user[4] == 'Admin':
                return render_template('Admin_vendor.html')
            elif user[4] == 'Vendor':
                return render_template('Admin_vendor.html')
            else:
                return render_template('Customer.html')
    else:
        return render_template('Login.html')


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    # Attempt to remove user data from session and redirect to login page
    try:
        session.pop('username', None)
        flash('You have successfully logged out.', 'success')
    except KeyError:
        flash('You were not logged in to begin with.', 'error')
    return redirect(url_for('Login'))


@app.route("/Registration", methods=['GET', 'POST'])
def Registration():
    if request.method == 'POST':
        # Get registration form data and insert into database
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        account_type = request.form['account_type']
        query = text(
            "INSERT INTO accounts(username,password,email,account_type)"
            "VALUES(:username, :password, :email, :account_type)")
        params = {"username": username, "password": password, "email": email, "account_type": account_type}
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


@app.route('/cart', methods=['GET', 'POST'])
def cart(conn = engine.connect()):
    if request.method == 'POST':
        query = text("SELECT * FROM products")
        result = conn.execute(query)
        product = []
        for row in result:
            product.append(row)
        max_cart_id =  text("SELECT MAX(cart_id) AS max_id FROM cart")
        results = conn.execute(max_cart_id).fetchone()
        max_id = results[0] if results[0] is not None else 1
        max_id = int(max_id)
        new_id = max_id + 1
        cart_id = new_id
        item_id = request.form['product_id']
        product_name = request.form['product_name']
        product_type = request.form['product_type']
        product_quantity = request.form['product_quantity']
        product_cost = request.form['product_cost']
        vendor_name = request.form['vendor_name']
        img_url = request.form['img_url']
        shopper_id = session['id']
        status = 'open'
        Cart_query = text("SELECT cart_id FROM cart WHERE shopper_id = :shopper_id AND status = 'open'")
        Cart_result = conn.execute(Cart_query, {"shopper_id": shopper_id}).fetchone()
        if Cart_result:
            with engine.connect() as conn:
                cart_id = Cart_result[0]
                Item_query = text("SELECT * FROM cart WHERE cart_id = :cart_id AND item_id = :item_id")
                Item_result = conn.execute(Item_query,{"cart_id": cart_id, "item_id": item_id}).fetchone()
            if Item_result:
                previous_amount = int(Item_result[4])
                new_amount = previous_amount + int(product_quantity)
                update_query = text("UPDATE cart SET product_quantity = :new_amount "
                                    "WHERE cart_id = :cart_id AND item_id = :item_id")
                update_params = {
                    "new_amount": new_amount,
                    "cart_id": cart_id,
                    "item_id": item_id
                }
                with engine.connect() as conn:
                    conn.execute(update_query, update_params)
                    conn.commit()
            else:
            #Add an item to exisiting cart
                query = text("INSERT INTO cart (cart_id,"
                         " shopper_id, "
                         "item_id, "
                         "product_name, "
                         "product_type, "
                         "product_cost, "
                         "product_quantity, "
                         "vendor_name, "
                         "img_url, "
                         "ordered_by, "
                         "status) "
                            "VALUES (:cart_id, "
                         ":shopper_id, "
                         ":item_id, "
                         ":product_name, "
                         ":product_type, "
                         ":product_cost, "
                         ":product_quantity, "
                         ":vendor_name, "
                         ":img_url, "
                         ":ordered_by, "
                         ":status)")
                params = {
                "cart_id": cart_id,
                "shopper_id": shopper_id,
                "item_id": item_id,
                "product_name": product_name,
                "product_type": product_type,
                "product_cost": product_cost,
                "product_quantity": product_quantity,
                "vendor_name": vendor_name,
                "img_url": img_url,
                "ordered_by": session['username'],
                "status": status
                }
                with engine.connect() as conn:
                    conn.execute(query, params)
                    conn.commit()
            return redirect(url_for('Products'))
        else:
        #Create a cart
            query = text("INSERT INTO cart (cart_id,"
                     " shopper_id, "
                     "item_id, "
                     "product_name, "
                     "product_type, "
                     "product_cost, "
                     "product_quantity, "
                     "vendor_name, "
                     "img_url, "
                     "ordered_by, "
                     "status) "
                     "VALUES (:cart_id, "
                     ":shopper_id, "
                     ":item_id, "
                     ":product_name, "
                     ":product_type, "
                     ":product_cost, "
                     ":product_quantity, "
                     ":vendor_name, "
                     ":img_url, "
                     ":ordered_by, "
                     ":status)")
            params = {
                "cart_id": cart_id,
                "shopper_id": shopper_id,
                "item_id": item_id,
                "product_name": product_name,
                "product_type": product_type,
                "product_cost": product_cost,
                "product_quantity": product_quantity,
                "vendor_name": vendor_name,
                "img_url": img_url,
                "ordered_by": session['username'],
                "status": status
            }
            with engine.connect() as conn:
                conn.execute(query, params)
                conn.commit()
            return render_template("Products.html")

@app.route('/view_cart')
def view_cart():
    if 'id' in session:
        shopper_id = session['id']
        with engine.connect() as conn:
            query = text("SELECT * FROM cart WHERE shopper_id = :shopper_id AND status = 'open'")
            items = conn.execute(query, {"shopper_id": shopper_id}).fetchall()
        return render_template('cart.html', items=items)
    else:
        return redirect(url_for('login'))

@app.route('/remove_item/<int:item_id>', methods=['POST'])
def remove_item(item_id):
    with engine.connect() as conn:
        query = text("DELETE FROM cart WHERE item_id = :item_id")
        conn.execute(query, {"item_id": item_id})
        conn.commit()
    return redirect(url_for('view_cart'))

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

@app.route('/orders')
def orders():
    if request.method == 'POST':

        return render_template('orders.html', username=session['username'], orders=orders)

if __name__ == '__main__':
    app.run(debug=True)