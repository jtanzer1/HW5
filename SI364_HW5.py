## SI 364
## HW5

## Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy

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
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/jtanzerHW5"
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
app.config['MAIL_SUBJECT_PREFIX'] = '[Tweets App]'
app.config['MAIL_SENDER'] = 'Admin <si364email@gmail.com>' # TODO fill in email
app.config['ADMIN'] = 'si364email@gmail.com'


# Set up Flask debug stuff
manager = Manager(app)
db = SQLAlchemy(app) # For database use
migrate = Migrate(app, db) # For database use/updating
manager.add_command('db', MigrateCommand) # Add migrate
mail = Mail(app)
# TODO: Run commands to create your migrations folder and get ready to create a first migration, as shown in the textbook and in class.

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
#########
######### Everything above this line is important/useful setup, not problem-solving.
#########
#########

##### Set up Models #####

# Association table - Tweets and Hashtags
tweet_hashtags = db.Table('tweet_hashtags', db.Column('tweet_id', db.Integer, db.ForeignKey('tweets.id')), db.Column('hashtag_id', db.Integer, db.ForeignKey('hashtags.id')))

# Tweet model
class Tweet(db.Model):
    __tablename__ = "tweets"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(285))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    hashtags = db.relationship('Hashtag', secondary=tweet_hashtags, backref=db.backref('tweets', lazy='dynamic'),lazy='dynamic')

    def __repr__(self):
        return "{}, (ID: {})".format(self.text,self.id)

# TODO: Add and run a  migration so that each twitter username also saves an associated email.
# User model
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True) ## -- id (Primary Key)
    twitter_username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    def __repr__(self):
        return "{} (ID: {})".format(self.twitter_username,self.id)

# Hashtag model
class Hashtag(db.Model):
    __tablename__ = 'hashtags'
    id = db.Column(db.Integer, primary_key=True) ## -- id (Primary Key)
    text = db.Column(db.String, unique=True) ## -- text (Unique=True) #represents a single hashtag (like UMSI)

    def __repr__(self):
        return "{} (ID: {})".format(self.text,self.id)


##### Set up Forms #####

# TODO: Add a field in the form for a user to enter their email (the email that goes with the twitter username entered).
# TODO: Edit the template that renders the form so that email is also asked for!
class TweetForm(FlaskForm):
    text = StringField("What is the text of your tweet? Please separate all hashtags with commas in this case. e.g. 'Yay Python #python, #programming, #awesome' ", validators=[Required()])
    username = StringField("What is your Twitter username?",validators=[Required()])
    email= StringField("What is your email?", validators=[Required()])
    submit = SubmitField('Submit')


##### Helper functions

### For database additions / get_or_create functions
## Write get_or_create functions for each model -- Tweets, Hashtags, and Users.
## -- Tweets should be identified by their text and user id,(e.g. if there's already a tweet with that text, by that user, then return it; otherwise, create it)
## -- Users should be identified by their username (e.g. if there's already a user with that username, return it, otherwise; create it)
## -- Hashtags should be identified by their text (e.g. if there's already a hashtag with that text, return it; otherwise, create it)

# TODO: Edit get_or_create_user (AND get_or_create_tweet -- see below) as necessary to store a user's email as well as their twitter username. The get_or_create_user function should accept an email as input and deal with it appropriately to save it as part of a User row. Each user (from now on) has an email! This should be a small change to how the function currently works.
def get_or_create_user(db_session, username, email):
    user = db_session.query(User).filter_by(twitter_username=username, email= email).first()
    if user:
        return user
    else:
        user = User(twitter_username=username, email =email)
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

# TODO: You will need to make changes in this function as well, to address users having emails. See above. What do you need to change to make sure get_or_create_user is *invoked* correctly, including saving an email? Does anything need to change about the input to get_or_create_tweet, and *its* invocations?
def get_or_create_tweet(db_session, input_text, username, email):
    tweet = db_session.query(Tweet).filter_by(text=input_text, user_id=get_or_create_user(db_session, username,email).id).first()
    if tweet:
        return tweet
    else:
        user = get_or_create_user(db_session, username, email)
        tweet = Tweet(text=input_text, user_id=user.id)
        for text in input_text.split(','):
            if "#" in text.strip():
                pos = text.find('#')
                word = text[pos:].replace("#", '')
                hashtag = get_or_create_hashtag(db_session, word.strip())
                tweet.hashtags.append(hashtag)
        db_session.add(tweet)
        db_session.commit()
        return tweet

##### Controllers (view functions) #####

## Error handling routes
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# TODO: Edit the index route so that, when a tweet is saved by a certain user, that user gets an email. Use the send_email function (just like the one in the textbook) that you defined above.
# NOTE: You may want to create a test gmail account to try this out so testing it out is not annoying. You can also use other ways of making test emails easy to deal with, as discussed in class!
## This is also very similar to example code.
@app.route('/', methods=['GET', 'POST'])
def index():
    tweets = Tweet.query.all()
    num_tweets = len(tweets)
    form = TweetForm()
    if form.validate_on_submit():
        if db.session.query(Tweet).filter_by(text=form.text.data, user_id= (get_or_create_user(db.session, form.username.data, form.email.data).id)).first():
            flash("You've already saved that tweet by this user!")
        else:

            get_or_create_tweet(db.session, form.text.data, form.username.data, form.email.data)
            send_email(app.config['ADMIN'], 'New Tweet',
                           'mail/new_tweet', tweet=form.text.data)
        return redirect(url_for('see_all_tweets'))
    return render_template('index.html', form=form,num_tweets=num_tweets)

@app.route('/all_tweets')
def see_all_tweets():
    all_tweets = []
    tweets = Tweet.query.all()
    for t in tweets:
        user = User.query.filter_by(id=t.user_id).first()
        all_tweets.append((t.text, user.twitter_username))
    return render_template('all_tweets.html', all_tweets=all_tweets)

@app.route('/all_users')
def see_all_users():
    all_users = []
    users = User.query.all()
    all_tweets = [(Tweet.query.filter_by(user_id=user.id).count(), user.twitter_username) for user in users]
    return render_template('all_tweets.html', all_tweets=all_tweets)

if __name__ == '__main__':
    db.create_all()
    manager.run() # Run with this: python main_app.py runserver
    # Also provides more tools for debugging
