from flaskproj import db, login_manager
from datetime import datetime
from flask_login import UserMixin

#current_user 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User Table
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    profile_picture = db.Column(db.String(100), nullable=True, default='default.jpg')
    
    posts = db.relationship('Post', backref='author', lazy=True)
    
    # one to many
    #to access the User objects that sent the friend requests.
    friend_requests_sent = db.relationship(
        "Friend",
        foreign_keys="Friend.user_id",
        backref="sent_friend_requests",
        lazy="dynamic",
    )
    friend_requests_received = db.relationship(
        "Friend",
        foreign_keys="Friend.friend_id",
        backref="receiver_user",
        lazy="dynamic",
    )
    
    friends = db.relationship(
        'Friend',
        foreign_keys='Friend.user_id',
        backref=db.backref('user', lazy='joined'),
        cascade='all, delete-orphan'
    )
    def get_friends(self):
        friend_ids = [friend.friend_id for friend in self.friends if friend.status == 'accepted']
        return User.query.filter(User.id.in_(friend_ids)).all()
    
    def is_friend(self, user):
        return Friend.query.filter_by(user_id=self.id, friend_id=user.id).first() is not None
    
    # dunder/magic method for print user object
    def __repr__(self):
        return f"(username: {self.username}, email: {self.email})"

# Post Table
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now())
    privacy = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # dunder/magic method for print user object
    def __repr__(self):
        return f"{self.title}, {self.content}, {self.date_posted}"
    
    

# Friend Table
class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #sender
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #receiver
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending') 

    sender = db.relationship("User", foreign_keys=[user_id])
    receiver = db.relationship("User", foreign_keys=[friend_id])

    def __repr__(self):
        return f"(user_id: {self.user_id}, friend_id: {self.friend_id})"         


