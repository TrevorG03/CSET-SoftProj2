from flask import Flask, render_template, request, redirect, url_for,session
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
app = Flask(__name__)
conn_str = "mysql://root:Treyjg2121@localhost/bank_accounts"
engine = create_engine(conn_str, echo = True)
conn = engine.connect()
app.config['SECRET_KEY'] = 'BigSecret'
@app.route("/", methods=['GET','POST'])
def index():
    return render_template("index.html")

@app.route("/Login", methods=['GET','POST'])
def Login():
    return render_template("Login.html")

@app.route("/Registration", methods=['GET','POST'])
def Registration():
    return render_template("Registration.html")

if __name__ == '__main__':
    app.run(debug=True)