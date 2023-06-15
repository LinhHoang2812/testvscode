from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory,session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user





login_manager = LoginManager()
app = Flask(__name__)

app.secret_key = 'barboncino'
app.config['SECRET_KEY'] = 'dexterisacutedog'
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager.init_app(app)

##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB. 
db.create_all()





@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():

    return render_template("index.html")


@app.route('/register',methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        all_users = User.query.all()
        all_emails = [ user.email for user in all_users]
        if email in all_emails:
            flash('You have already registered with this email, please log in instead')
            return redirect(url_for('login'))
        password = generate_password_hash(request.form["password"],method='pbkdf2:sha256', salt_length=8)
        new_user = User(name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return render_template("secrets.html",name=name.title())
    return render_template("register.html")


@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user == None:
            flash("The email doesnt exist, please try again")
            return redirect(url_for('login'))

        else:
            if check_password_hash(user.password,request.form["password"]):
                login_user(user)
                return render_template("secrets.html")
            else:
                flash('Password incorrect! Please try again')
                return redirect(url_for('login'))




    return render_template("login.html")



@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("login.html")


@app.route('/download/<filename>')
@login_required
def download(filename):
    return send_from_directory("static/files",filename, as_attachment=True)



if __name__ == "__main__":
    app.run(debug=True)