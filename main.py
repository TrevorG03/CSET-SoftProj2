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
        password = request.form['password']
        account_type = request.form['account_type']
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
    return render_template('Products.html')

@app.route('/Accounts', methods=['GET','POST'])
def Accounts():
    return render_template('Accounts.html')

@app.route('/VendorAdd', methods=['GET','POST'])
def AddProducts():
    return render_template('VendorAdd.html')

if __name__ == '__main__':
    app.run(debug=True)