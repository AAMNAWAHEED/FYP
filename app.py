from flask import Flask,render_template,request,session,url_for,redirect,flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import re
import flask_login 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__,template_folder="template")
app.config['SQLALCHEMY_DATABASE_URI']   ='mysql+pymysql://root:root@localhost/FYP'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager(app)
login_manager.login_view = 'login'
# Replace this with your user loading function
@login_manager.user_loader
def load_user(id):
    query = text("select * from customer where customer_id = :id")
    res = db.session.execute(query,{'id':id})
    user = res.fetchone()
    if user:
        return User(user[0], [1])  # Adjust according to your user schema

    return None


class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username  

def authenticate(email, password):
    query = text("SELECT * FROM customer WHERE email = :email and password = :password")
    res = db.session.execute(query, {'email':email,'password':password})
    user = res.fetchone()
    if user:
        user =  User(user[0], user[1])  # Adjust according to your user schema
        return user
    return None

#sesssion
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)
import uuid
def generate_session_id():
    return str(uuid.uuid4())
save_order ={}


def sorted_products(category,order_col,order):
    query = text("select product_id,name,image1_url,price from product where category = {category} order by {order_col} {order}")
    res = db.session.execute(query)
    rows = res.fetchall()
    return rows


db = SQLAlchemy(app)
@app.route("/")
def main():
    orderPlaced = request.args.get('orderPlaced', False)
    return render_template("mainPage.html",orderPlaced = orderPlaced)

#aacount

@app.route("/account")
def account():
    if current_user.is_authenticated:
       return render_template('dashboard.html')
    else:
        return render_template("account.html")

@app.route("/login",methods=['GET','POST'])
def login():
    #if current_user.is_authenticated:
    #    return "logged in dashboard"
    #verify name and password
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        #authentication
        user = authenticate(email, password)
        if user:
            login_user(user)
            flash('Login successful', 'success')
            return render_template('dashboard.html')
        else:
            return "invalid email or password"

@app.route('/logout')
#@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('Logout successful', 'success')
        return redirect(url_for('main'))
    else:
        return "have logged out"

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
            return "email has taken"
#unstitch
@app.route("/unstitch",methods=['GET','POST'])
def unstitch():
    #print(f"{save_order}fbjsdhfiyeut7348rhsdjkfnuidygu8dykdhgeruigysdi")
    if request.method == 'POST':
        #save this order
        order_by = request.form['sort-order']
        save_order['sort-order'] = order_by
    else:
        if 'sort-order' not in save_order:
            order_by = request.args.get('sort-order',default='ASC-price') 
        else:
            order_by = save_order['sort-order']
    order = order_by.split('-')[0]
    order_col = order_by.split('-')[1]
    print(f"{order},{type(order)},{order_col},{type(order_col)}")


    page_number = request.args.get('page', default=1, type=int)
    category = request.args.get('category',type=int)
    limit= 9
    offset = (page_number-1)*limit
    category_mappings = {
            1: 'stitch',
            2:'unstitch',
            3:'fragrance',
            4:'footwear',
            5:'bottom'
            }
        
    category_name = category_mappings.get(category)
    query = text(f"select product_id,name,image1_url,price from product where category = :category order by {order_col} {order} limit :limit offset :offset")
    params = {
        'category':category,
        'limit':limit,
        'offset':offset
        }
    res = db.session.execute(query,params)
    rows = res.fetchall()

    query = text("select count(*) from product where category = :category")
    res = db.session.execute(query,{'category':category})
    total_items = res.scalar()

    query = text("select MIN(price) from product where category = :category")
    res = db.session.execute(query,{'category':category})
    starting_price = res.scalar()

    query = text("select image1_url from product where category = :category limit 1")
    res = db.session.execute(query,{'category':category})
    image = res.fetchone()

    return render_template("unstitch1.html",products = rows,category = category,category_name=category_name,starting = starting_price,image=image[0],total_items=total_items)

@app.route("/viewProduct/<int:product_id>")
def viewProduct(product_id):
    query = text("SELECT * from product where product_id = :product_id")
    res = db.session.execute(query,{'product_id':product_id})
    rows = res.fetchone()
    #if stitch category
    size_chart = None
    if rows[5] == 1:
        query = text("select * from cloth_size where product_id = :product_id")
        res = db.session.execute(query,{'product_id':rows[0]})
        size_chart = res.fetchall()
    print(size_chart)

    return render_template("viewProduct.html",product = rows,size_chart = size_chart)

@app.route("/uploadimage",methods=['Get','Post'])
def uploadimage():
    if request.method == 'POST':
        image = request.form['image']
        return "cheking"

@app.route("/addtocart/<int:product_id>",methods=['GET','POST'])
def addtocart(product_id):
    if request.method == 'POST':
        quantity = request.form['quantity']
        if current_user.is_authenticated:
            id = current_user.id
            query = text("insert into shopping_session(user_id,product_id,quantity) values(:id,:product_id,:quantity)")
            res = db.session.execute(query,{'id':id,"product_id":product_id,"quantity":quantity})
            db.session.commit()
            return "user successfully added to cart"
            #return "logged in dashboard"
        elif 'session_id' not in session:
            session['session_id'] = generate_session_id()
        else:
            query = text("insert into shopping_session(session_id,product_id,quantity) values(:session_id,:product_id,:quantity)")
            res = db.session.execute(query,{'session_id':session['session_id'],"product_id":product_id,"quantity":quantity})
            db.session.commit()
        #print(f"{product_id}dshjkyweiu")
        return redirect(url_for('viewProduct',product_id = product_id))
        #return "successfully added to cart"
    return "something went wrong"


@app.route("/viewCart")
def viewCart():
    if current_user.is_authenticated:
        id = current_user.id

        query = text("SELECT product.product_id, product.name, product.image1_url,shopping_session.quantity,shopping_session.id,shopping_session.total FROM product JOIN shopping_session ON product.product_id = shopping_session.product_id WHERE shopping_session.user_id = :id ")
        res = db.session.execute(query,{'id':id})
        rows = res.fetchall()

        query = text("select SUM(total) from product join shopping_session ON product.product_id = shopping_session.product_id where user_id =:id")
        res = db.session.execute(query,{'id':id})
        total = res.scalar()
    elif 'session_id' not in session:
        return "no cart"
    else:
        query = text("SELECT product.product_id, product.name, product.image1_url,shopping_session.quantity,shopping_session.id,shopping_session.total FROM product JOIN shopping_session ON product.product_id = shopping_session.product_id WHERE shopping_session.session_id = :session_id ")
        res = db.session.execute(query,{'session_id':session['session_id']})
        rows = res.fetchall()
        #total
        query = text("select SUM(total) from product join shopping_session ON product.product_id = shopping_session.product_id where session_id =:session_id")
        res = db.session.execute(query,{'session_id':session['session_id']})
        total = res.scalar()
    if total is None:
        total = 0
    return render_template("viewCart.html",products = rows,total=total)

@app.route("/delFromCart/<int:id>")
def delFromCart(id):
    query = text(f"delete from shopping_session where id = {id}")
    res = db.session.execute(query)
    db.session.commit()
    return  redirect(url_for('viewCart'))
@app.route("/addinfo")
def info():
    if current_user.is_authenticated:
        id = current_user.id
        query = text("select SUM(total) from product join shopping_session ON product.product_id = shopping_session.product_id where shopping_session.user_id =:id")
        res = db.session.execute(query,{'id':id})
        total = res.scalar()

        query = text("select * from customer where customer_id = :id")
        res = db.session.execute(query,{'id':id})
        loggedin_data = res.fetchone()
    else:
        query = text("select SUM(total) from product join shopping_session ON product.product_id = shopping_session.product_id where session_id =:session_id")
        res = db.session.execute(query,{'session_id':session['session_id']})
        total = res.scalar()
    shipping = 200
    grand_total = total + shipping



    return render_template("addInfo.html",total=total,shipping=shipping,grand_total=grand_total)

@app.route("/placeorder",methods= ['GET','POST'])
def placeorder():
    if request.method=='POST':
        f_name  =request.form['f_name']
        l_name  =request.form['l_name']
        number = request.form['mobile']
        country = request.form['country']
        address = request.form['address']
        city = request.form['city']
        payment_method = request.form['option']

        if current_user.is_authenticated:
            id = current_user.id
            #update customer details
            query = text("update customer set mobile_number = :number, country = :country,address = :address,city = :city where customer_id = :id")
            params = {
            'number':number,
            'country':country,
            'address':address,
            'city':city,
            'id':id
            }
            res = db.session.execute(query,params)
            db.session.commit()
            #session_id = None
            query = text("insert into orders (customer_id) values (:customer_id)")
            res = db.session.execute(query,{'customer_id':id})
            db.session.commit()
            #delete from shopping_session
            query = text("delete from shopping_session where user_id = :id")
            res = db.session.execute(query,{'id':id})
            db.session.commit()
            
        else:
            session_id = session['session_id']
            #insert customer details
            query = text("insert into customer(first_name,last_name,mobile_number,city,country,address) values(:f_name,:l_name,:number,:country,:address,:city)")
            params = {
            'f_name':f_name,
            'l_name':l_name,
            'number':number,
            'country':country,
            'address':address,
            'city':city
            }
            res = db.session.execute(query,params)
            db.session.commit()
            id = res.lastrowid #problemmmmmmmm
            #2-insert into orders table
            query = text("insert into orders(session_id) values (:session_id)")
            res = db.session.execute(query,{'session_id':session['session_id']})
            db.session.commit()
            #dekete from shopping_session
            query = text("delete from shopping_session where session_id = :session_id")
            res = db.session.execute(query,{'session_id':session['session_id']})
            db.session.commit()
        orderPlaced = True
        return redirect(url_for('main',orderPlaced = orderPlaced))
    return "something went wrong"


if __name__ =="__main__":
    app.run(debug=True,port=5001)