from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_login import UserMixin
from hashlib import md5

followers = db.Table(
    'followers',
    db.Column('follower', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True, unique=True)
    username = db.Column(db.String(64), index=True)
    password = db.Column(db.String(128))
    points = db.Column(db.Integer, default=0)
    riddles = db.relationship('Riddle', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User', 
        secondary = followers,
        primaryjoin = (followers.c.follower == id),
        secondaryjoin = (followers.c.followed == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    def __repr__(self):
        return '< User : {} >'.format(self.email)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        return not self.followed.filter(
            followers.c.followed == user.id).first() is None
    
    def add_point(self): self.points += 1

    def followed_riddles(self):
        return Riddle.query.join(
            followers, (followers.c.followed == Riddle.user_id)).filter(
                followers.c.follower == self.id).order_by(
                    Riddle.timestamp.desc())
    
    def followers_count(self):
        return db.session.query(followers.c.follower).filter(followers.c.followed == self.id).count()

    def get_place(self):
        sub = (db.session
            .query(
                User.id,
                db.func.row_number().over(order_by=db.desc(User.points)).label('pos'))
            .subquery())
        return db.session.query(sub.c.pos).filter(sub.c.id==self.id).scalar()

class Riddle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    answer = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    theme = db.Column(db.String(7))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answers = db.relationship("Solution", lazy='dynamic')

    def is_answered(self, user):
        return self.answers.filter(Solution.user_id == user.id).count() != 0
    
    def get_answer(self, user):
        return self.answers.filter(Solution.user_id == user.id).first().answer == self.answer

    def num_answers(self):
        return self.answers.filter(Solution.riddle_id == self.id).count()

    def is_dark(self):
        n = int(int(self.theme[1:3], 16) > 128) + int(int(self.theme[3:5], 16) > 128) + int(int(self.theme[5:7], 16) > 128)
        return n<2

class Solution(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    riddle_id = db.Column(db.Integer, db.ForeignKey('riddle.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer = db.Column(db.String(80))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))