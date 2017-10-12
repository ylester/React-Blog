from flask import Flask, render_template, request, json, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
# from datetime import datetime
from flask.ext.login import LoginManager
from flask.ext.login import UserMixin

login_manager = LoginManager()
login_manager.login_view = "users.login"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new.db'
app.secret_key = 'key'

db = SQLAlchemy(app)
login_manager.init_app(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    pwd = db.Column(db.String(54))
    #authenticated = db.Column(db.Boolean, default=False)
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
	self.set_password(password)
        self.authenticated = False
       # self.posts = posts
    
    def set_password(self, password):
        self.pwd = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwd, password)

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated
 
    @property
    def is_active(self):
        """Always True, as all users are active."""
        return True
 
    @property
    def is_anonymous(self):
        """Always False, as anonymous users aren't supported."""
        return False
 
    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        """Requires use of Python 3"""
        return str(self.id)

    def __repr__(self):
        return '<User %r, %r, %r>' % (self.name, self.email, self.pwd)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(140))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, timestamp, user_id):
        self.title = title
        self.body = body
        self.timestamp = timestamp
        self.user_id = user_id

    def __repr__(self):
        return '<Post %r , %r>' % (self.title, self.body)

# class LoginForm(Form):
#     email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=40)])
#     password = PasswordField('Password', validators=[DataRequired()])


####################################################################

@app.route("/")
@app.route("/main")
@app.route("/index")
def main():
    if session.get('logged_in'):
        "You are already logged in %s" %(User.name)

    return render_template('index.html')


@app.route('/showSignUp', methods=['GET', 'POST'])
def showSignUp():
    if request.method == 'POST':
        db.session.add(User(request.form['name'],request.form['email'], request.form['pwd']))
        db.session.commit()
        return 'Thank you ' + request.form['name'] + ', your user is created!'
    return render_template('signup.html')


@app.route('/showSignin', methods=['GET', 'POST'])
def showSignin():
    if 'email' in session:
        flash("You're already logged in!") # %(session['name'])
        redirect(url_for('userHome'))

    if request.method == "POST":
        myUser = User.query.filter_by(email=request.form['email']).first()
        passhash = myUser.check_password(request.form['pwd'])
        if passhash == True and myUser.email is not None:
            session['logged_in'] = True
            return render_template('userHome.html')
        else:
            return "Incorrect Login"
            
    return render_template('signin.html')


@app.route('/showAddBlog', methods=['GET', 'POST'])
def showAddBlog():
    if request.method == 'POST':
        if 'email' in session:
            user_id = User.query.filter_by(name=request.form['name']).first().id
            blog_post = Post(request.form['inputTitle'],request.form['inputDescription'], now.year, user_id)
            db.session.add(blog_post)
            db.session.commit()
            return "Blog Added!!!" 
    return render_template('addBlog.html')

@login_manager.user_loader
def load_user(user_id):
    #return User.get(user_id)
    return User.query.filter(User.id == int(user_id)).first()

@app.route('/homepage')
def homepage():
    return render_template("userHome.html")

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect('/')

def user_loader(user_id):
    return User.query.get(user_id)


if __name__ == "__main__":
   db.create_all()
   app.run(debug=True)
