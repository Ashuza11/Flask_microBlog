from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from flask_login import UserMixin
from time import time
import jwt
from app import app
from app import login


# Followers association table 
followers = db.Table('follower',
                db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
            )

class User(UserMixin, db.Model):
    """
        A class used to represent the user
        ....
         Attributes
        -----------
        id: int 
            unique value automatically assigned by 
            the databse.
        email: str or Varchar
            email adress of the user
        password_hash: str or varchar
            A user hashed password 
        posts: one to many relationship
            link user to posts(not a db field)

    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        """Set the hashed password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Chec wheter the hashed pwd matches the pwd"""
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        """Generates and returns the avatar URLs of user avatar img"""
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
    
    def follow(self, user):
        """Add relationship (follow a user)"""
        if not self.is_following(user):
            self.followed.append(user)
            
    def unfollow(self, user):
        """Remove relationship (unfollow a user)"""
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        """Make sure there is no duplicates for follow and unfollow"""
        return self.followed.filter(
            followers.c.followed_id == user.id
        ).count() > 0

    def followed_posts(self):
        """Qusery to get user's own posts."""
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
    
    def get_reset_password_token(self, expires_in=600):
        """Generate token for changing user email"""
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        """Verify if user exixt before password reset"""
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithm=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
        
    def __repr__(self):
        return '<User {}>'.format(self.username)



class Post(db.Model):
    """
        A class used to represent posts
        ....
         Attributes
        -----------
        id: int 
            unique value automatically assigned by 
            the databse.
        body: str or Varchar
            Contentes of the posts
        timestamp: date and time
            Date and time the post was 
            posted 
        user_id: reference to user id 
            link posts to user

    """
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
    

