from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
app = Flask(__name__)
app.config['SECRET_KEY'] = 'BigSecret'
conn_str = "mysql://root:Treyjg2121@localhost/ecommerce"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

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
            return render_template('Accounts.html')
        if account_type == "Vendor":
            return render_template('VendorAdd.html')
        if account_type == "User":
            return render_template("Products.html")
    else:
        return render_template("Login.html")

@app.route("/logout", methods =['GET','POST'])
def logout():
    session.pop('id', None)
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

@app.route('/Products', methods=['GET','POST'])
def Products():
    if request.method == 'POST':
        return render_template('Products.html')
    else:
        query = text("SELECT * FROM product_info")
        with engine.connect() as conn:
            products = conn.execute(query).fetchall()
        return render_template('Products.html', products=products)

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

@app.route('/VendorAdd', methods=['GET','POST'])
def AddProducts():
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_type = request.form['product_type']
        product_cost = request.form['product_cost']
        img_url = request.form['img_url']
        query = text(
            "INSERT INTO product_info(product_name,product_type,product_cost,img_url)"
            "VALUES(:product_name, :product_type, :product_cost, :img_url)")
        params = {"product_name": product_name, "product_type": product_type, "product_cost": product_cost, "img_url": img_url}
        with engine.connect() as conn:
            conn.execute(query, params)
            conn.commit()
            return render_template("VendorAdd.html")
    else:
        return render_template("VendorAdd.html")

@app.route('/Chat', methods=['GET', 'POST'])
def Chat():
    if request.method == 'POST':
        Your_User = request.form['Your_User']
        username = request.form['username']
        account_type = request.form['account_type']
        messages = request.form['messages']
        query = text(
            "INSERT INTO Chats(Your_User,username,account_type,messages)"
            "VALUES(:Your_User, :username, :account_type, :messages)")
        params = {"Your_User" :Your_User,"username": username, "account_type": account_type, "messages": messages}
        with engine.connect() as conn:
            conn.execute(query, params)
            conn.commit()
        return render_template("Chat.html")
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
        return render_template('Show.html', chats=chats)
    else:
        return render_template('Show.html')

if __name__ == '__main__':
    app.run(debug=True)