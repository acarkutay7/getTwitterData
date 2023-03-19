from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required,current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from getdata import search_on_twitter

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean(), default = True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()
        if not user or not user.verify_password(password):
            error = "Incorrect username or password"
            return render_template('login.html', error=error)
        
        login_user(user)
        return redirect(url_for('welcome'))
    return render_template('login.html')

@app.route('/welcome', methods = ['GET','POST'])
@login_required
def welcome():
    if request.method == 'POST':
        search = request.form['search']
        print("Search key :",search)
        search_on_twitter(search)
    return render_template('welcome.html', name = current_user.username)

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        new_user = User(username = name, password = password, is_active = True)
        db.session.add(new_user)
        db.session.commit()
        return 'Thank you for signing up !'
    return render_template('signup.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # user = User(username='kutay', password='123', is_active = True)
        # db.session.add(user)
        # db.session.commit()
    app.run(debug=True)
