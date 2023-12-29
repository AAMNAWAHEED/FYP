from flask import Flask,render_template,request,session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import re

app = Flask(__name__,template_folder="C://Users//Waheed Akhtatr//Downloads//FYP//userWebsite//template")
app.config['SQLALCHEMY_DATABASE_URI']   ='mysql+pymysql://root:root@localhost/FYP'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#sesssion
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)
import uuid
def generate_session_id():
    return str(uuid.uuid4())



db = SQLAlchemy(app)
@app.route("/")
def main():
    return render_template("mainPage.html")

#aacount

@app.route("/account")
def account():
    return render_template("account.html")

@app.route("/login",methods=['GET','POST'])
def login():
    #verify name and password
    if request.method =='POST':
        name = request.form['username']
        password = request.form['password']
        query = text("select * from customer where first_name=:name and password= :password")
        res = db.session.execute(query,{"name":name,"password":password})
        rows = res.fetchall()
        if rows:
            return "valid"
        else:
            return "invalid"


@app.route("/create-account")
def create():
    return render_template("createAccount.html")

@app.route("/register",methods=['GET','POST'])
def register():
    if request.method=='POST':
        f_name = request.form['firstname']
        l_name = request.form['lastname']
        gender = request.form['gender']
        dob= request.form['dob']
        mobile_number = request.form['mob-number']
        email = request.form['email']
        password = request.form['password']
        confirm_pass = request.form['confirm_password']
        #verify email re and not in db
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if f_name == None or l_name ==None or gender==None or dob==None or mobile_number==None or email == None or password==None or confirm_pass ==None:
            return "fill all values"
        if re.match(pattern, email) == None:
            return "wrong email"
        else:
            query = text("select * from customer where email=:email")
            res = db.session.execute(query,{"email":email})
            rows = res.fetchall()
        print(len(rows))
        if len(rows)==0 and password == confirm_pass:
            #insert into db
            query = text("insert into customer(first_name,last_name,gender,dob,mobile_number,email,password) values(:f_name,:l_name,:gender,:dob,:mobile_number,:email,:password)")
            params = {
                "f_name": f_name,"l_name": l_name,"gender": gender,"dob": dob,"mobile_number": mobile_number,"email": email,"password": password
            }
            db.session.execute(query,params)
            db.session.commit()
            return "account created successfullt"
        else:
            return "no"
#unstitch
@app.route("/unstitch")
def unstitch():
    query = text("select product_id,name,image1_url,price from product limit 9")
    res = db.session.execute(query)
    rows = res.fetchall()

    return render_template("unstitch1.html",products = rows)

@app.route("/viewProduct/<int:product_id>")
def viewProduct(product_id):
    query = text("SELECT * from product where product_id = :product_id")
    res = db.session.execute(query,{'product_id':product_id})
    rows = res.fetchone()
    return render_template("viewProduct.html",product = rows)

@app.route("/addtocart/<int:product_id>",methods=['GET','POST'])
def addtocart(product_id):
    if request.method == 'POST':
        quantity = request.form['quantity']
        if 'session_id' not in session:
            session['session_id'] = generate_session_id()
        query = text("insert into shopping_session(session_id,product_id,quantity) values(:session_id,:product_id,:quantity)")
        res = db.session.execute(query,{'session_id':session['session_id'],"product_id":product_id,"quantity":quantity})
        db.session.commit()

        return f"{quantity}product added to cart"
    return "not added"


@app.route("/viewCart")
def viewCart():
    if 'session_id' not in session:
        return "no cart"
    else:
        query = text("SELECT product.product_id, product.name, product.price, product.image1_url,shopping_session.quantity FROM product JOIN shopping_session ON product.product_id = shopping_session.product_id WHERE shopping_session.session_id = :session_id ")
        res = db.session.execute(query,{'session_id':session['session_id']})
        rows = res.fetchall()
        return render_template("viewCart.html",products = rows)

@app.route("/unstitch2")
def unstitch2():
    query = text("select name,image_url,price from product  limit 9 offset 9")
    res = db.session.execute(query)
    rows = res.fetchall()
    return render_template("unstitch1.html",products = rows)

@app.route("/unstitch3")
def unstitch3():
    query = text("select name,image_url,price from product  limit 4 offset 8")
    res = db.session.execute(query)
    rows = res.fetchall()
    return render_template("unstitch1.html",products = rows)
    
if __name__ =="__main__":
    app.run(debug=True,port=5001)