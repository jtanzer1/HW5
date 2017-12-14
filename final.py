## SI 364
## HW5


## Import statements
import os
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask import jsonify, Flask, render_template, session, redirect, url_for, flash, request
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, Form
from wtforms import StringField, SubmitField, FileField, PasswordField, BooleanField, SelectMultipleField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user

from flask_migrate import Migrate, MigrateCommand

from flask_mail import Mail, Message
from threading import Thread
from werkzeug import secure_filename

# Configure base directory of app
basedir = os.path.abspath(os.path.dirname(__file__))

# Application configurations
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364(thisisnotsupersecure)'
## Create a database in postgresql in the code line below, and fill in your app's database URI. It should be of the format: postgresql://localhost/YOUR_DATABASE_NAME

## TODO: Create database and change the SQLAlchemy Database URI.
## Your Postgres database should be your uniqname, plus HW5, e.g. "jczettaHW5" or "maupandeHW5"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/jtanzerfinal"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# TODO: Add configuration specifications so that email can be sent from this application, like the examples you saw in the textbook and in class. Make sure you've installed the correct library with pip! See textbook.
# NOTE: Make sure that you DO NOT write your actual email password in text!!!!
# NOTE: You will need to use a gmail account to follow the examples in the textbook, and you can create one of those for free, if you want. In THIS application, you should use the username and password from the environment variables, as directed in the textbook. So when WE run your app, we will be using OUR email, not yours.
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587 #default
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'si364email@gmail.com'# TODO export to your environs -- may want a new account just for this. It's expecting gmail, not umich
app.config['MAIL_PASSWORD'] = 'Camp12955'
app.config['MAIL_SUBJECT_PREFIX'] = '[Movie List App]'
app.config['MAIL_SENDER'] = 'Admin <si364email@gmail.com>' # TODO fill in email
app.config['ADMIN'] = 'si364email@gmail.com'


# Set up Flask debug stuff
manager = Manager(app)
db = SQLAlchemy(app) # For database use
migrate = Migrate(app, db) # For database use/updating
manager.add_command('db', MigrateCommand) # Add migrate
mail = Mail(app)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)


## Set up Shell context so it's easy to use the shell to debug
def make_shell_context():
	return dict(app=app, db=db, Tweet=Tweet, User=User, Hashtag=Hashtag)
# Add function use to manager
manager.add_command("shell", Shell(make_context=make_shell_context))

# TODO: Write a send_email function here. (As shown in examples.)
def send_async_email(app, msg):
	with app.app_context():
		mail.send(msg)

def send_email(to, subject, template, **kwargs): 
	msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
				  sender=app.config['MAIL_SENDER'], recipients=[to])
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	thr = Thread(target=send_async_email, args=[app, msg]) # using the async email to make sure the email sending doesn't take up all the "app energy" -- the main thread -- at once
	thr.start()
	return thr


##### Set up Models #####





# User model

class List_Movies(db.Model):
	__tablename__ = "list_movie"
	id = db.Column(db.Integer, primary_key=True) 
	movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))
	list_id = db.Column(db.Integer, db.ForeignKey('lists.id'))

class User(UserMixin, db.Model):
	__tablename__ = "user"
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(64), unique=True)
	password_hash = db.Column(db.String(200), unique=True)    
	
	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

class Movie(db.Model):
	__tablename__ = 'movies'
	id = db.Column(db.Integer, primary_key=True) ## -- id (Primary Key)
	longdescription = db.Column(db.String)
	title = db.Column(db.String) ## -- text (Unique=True) 

class List(db.Model):
	__tablename__ = "lists"
	id = db.Column(db.Integer, primary_key=True)
	list_type= db.Column(db.String)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   
import requests
def getMovieSearch(movie):
	data =  requests.get("https://itunes.apple.com/search?entity=movie&term={}".format(movie)).json()["results"]
	for movie in data:
		found_movie = db.session.query(Movie).filter_by(title=movie["trackName"]).first()
		if found_movie:
			continue
		else:
			new_movie = Movie(longdescription = movie["longDescription"], title = movie["trackName"])
			db.session.add(new_movie)
			db.session.commit()
	return data


def get_or_create_list(list_type, user_id):
	lst = db.session.query(List).filter_by(list_type=list_type, user_id=user_id).first()
	if lst:
		return lst
	else:
		lst = List(list_type=list_type, user_id=user_id)
		db.session.add(lst)
		db.session.commit()
		return lst

def add_movie_to_list(title, user_id, list_type):
	lst_id = get_or_create_list(list_type, user_id).id
	movie_id = db.session.query(Movie).filter_by(title=title).first().id
	lst_movie = db.session.query(List_Movies).filter_by(movie_id=movie_id, list_id=lst_id).first()
	if lst_movie:
		return lst_movie
	else:
		lst_movie = List_Movies(movie_id=movie_id, list_id=lst_id)
		db.session.add(lst_movie)
		db.session.commit()
		return lst_movie


##### Set up Forms #####

class TweetForm(FlaskForm):
	text = StringField("What is the text of your tweet? Please separate all hashtags with commas in this case. e.g. 'Yay Python #python, #programming, #awesome' ", validators=[Required()])
	username = StringField("What is your Twitter username?",validators=[Required()])
	email= StringField("What is your email?", validators=[Required()])
	submit = SubmitField('Submit')


##### Helper functions



def get_or_create_user(db_session, password, email):
	user = db_session.query(User).filter_by(password=password, email= email).first()
	if user:
		return user
	else:
		user = User(password=password, email= email)
		db_session.add(user)
		db_session.commit()
		return user

def get_or_create_hashtag(db_session, hashtag_given):
	hashtag = db_session.query(Hashtag).filter_by(text = hashtag_given).first()
	if hashtag:
		return hashtag
	else:
		hashtag = Hashtag(text=hashtag_given)
		db_session.add(hashtag)
		db_session.commit()
		return hashtag

##### Controllers (view functions) #####

## Error handling routes
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500


class MovieForm(FlaskForm):
	searchWord= StringField("Enter a movie!", validators=[Required()])
	submit = SubmitField('Submit')

class AddToListForm(FlaskForm):
	addToSeen = SubmitField(label='Add to Seen List')
	addToWant = SubmitField(label='Add to Want to List')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class RegistrationForm(FlaskForm):
	email = StringField('Email:', validators=[Required(),Length(1,64),Email()])
	password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
	password2 = PasswordField("Confirm Password:",validators=[Required()])
	submit = SubmitField('Register User')

	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')


## Login setup
@app.route('/login',methods=["GET","POST"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(request.args.get('next') or url_for('index'))
		flash('Invalid username or password.')
	return render_template('login.html',form=form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out')
	return redirect(url_for('index'))

@app.route('/register',methods=["GET","POST"])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data,password=form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('You can now log in!')
		return redirect(url_for('login'))
	return render_template('register.html',form=form)

# App routes

@app.route("/")
@login_required
def index():
	return render_template("index.html")

@app.route("/list/to_see")
@login_required
def to_see():
	# To See List
	to_see_list = [db.session.query(Movie).filter_by(id=movie.movie_id).first() for movie in db.session.query(List_Movies).filter_by(list_id=get_or_create_list(list_type="toSee", user_id=current_user.id).id).all()]
	return render_template("toSeeList.html", toSee=to_see_list)

@app.route("/list/has_seen")
@login_required
def has_seen():
	# Has seen List
	has_seen_list = [db.session.query(Movie).filter_by(id=movie.movie_id).first() for movie in db.session.query(List_Movies).filter_by(list_id=get_or_create_list(list_type="hasSeen", user_id=current_user.id).id).all()]
	return render_template("hasSeenList.html", hasSeen=has_seen_list)
	

@app.route('/search', methods=['GET', 'POST'])
@login_required
def searchMovies():
	form = MovieForm()
	if form.validate_on_submit():
		moviesList = getMovieSearch(form.searchWord.data)
		return render_template("movieResults.html", movie_lst = moviesList, searchWord = form.searchWord.data)
	return render_template('movieSearch.html', form=form)

@app.route('/movie/<name>', methods = ["GET", "POST"])
@login_required
def longDescription(name):
	form = AddToListForm()
	if form.validate_on_submit():
		if form.addToSeen.data:
		
			add_movie_to_list(name, 1, "hasSeen")
		else:
			add_movie_to_list(name, 1, "toSee")	
		return redirect("/")
	return render_template("movieDescription.html", form = form, longDesc=getMovieSearch(name)[0]["longDescription"])

@app.route('/list/toSee')
@login_required
def to_see_api():
	to_see_list = [db.session.query(Movie).filter_by(id=movie.movie_id).first() for movie in db.session.query(List_Movies).filter_by(list_id=get_or_create_list(list_type="toSee", user_id=current_user.id).id).all()]
	emailList = [{"title": movie.title} for movie in to_see_list]
	send_email(current_user.email, "Your To See List", "mail/to_see", lst=[{"title": movie.title} for movie in to_see_list])
	return jsonify({
		"list" : emailList
		})

@app.route('/list/hasSeen')
@login_required
def has_seen_api():
	has_seen_list = [db.session.query(Movie).filter_by(id=movie.movie_id).first() for movie in db.session.query(List_Movies).filter_by(list_id=get_or_create_list(list_type="hasSeen", user_id=current_user.id).id).all()]
	emailList = [{"title": movie.title} for movie in has_seen_list]
	send_email(current_user.email, "Your Has Seen List", "mail/has_seen", lst=[{"title": movie.title} for movie in has_seen_list])
	return jsonify({
		"list" : emailList
		})

if __name__ == '__main__':
	db.create_all()
	manager.run() # Run with this: python main_app.py runserver
	# Also provides more tools for debugging
