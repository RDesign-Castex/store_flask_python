# imports

from itertools import product
from flask import Flask, redirect, render_template, request, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

# application init
db = SQLAlchemy()
def create_app():
  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
  app.config['SECRET_KEY'] = 'password'
  db.init_app(app)
  with app.app_context():
      db.create_all() 
  return app
app = create_app()    

#login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


#database tables
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255))
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Float)

    def __repr__(self):
        return f'<Product (self.title)>'
    
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))    

     
    
# routes
@app.route('/')
def home():
     products = Product.query.all()
     return render_template('home.html', products=products)


@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username = username).first()

        # check if user exists and password is correct
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        
        return 'Invalid username or password'
    return render_template('login.html')


#product routes
@app.route('/create_product', methods=['GET', 'POST'])
@login_required
def create_product():
   if request.method == 'POST':
       image = request.form.get('image')
       title = request.form.get('title')
       description = request.form.get('description')
       price = request.form.get('price')
       product = Product(image=image, title=title, description=description, price=price)
       db.session.add(product)
       db.session.commit()
       return redirect(url_for('home'))
   return render_template('create_product.html')
   

@app.route('/update_product/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
   if product:
         product = Product.query.get(product_id)
         product.image = request.form.get('image')
         product.title = request.form.get('title')
         product.description = request.form.get('description')
         product.price = request.form.get('price')
         db.session.commit()
         return redirect(url_for('home'))

@app.route('/delete_product/<int:product_id>', methods=['GET','POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:     
      db.session.delete(product)
      db.session.commit()
    return redirect(url_for('home'))

#run application
if __name__ == '__main__':
     
    app.run(debug=True)

