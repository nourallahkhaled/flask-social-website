from flaskproj import db, app
from flaskproj.models import User, Post
import sys

# Create Database
def create_db():
    with app.app_context():
        # you will have instance folder with site.db inside
        db.create_all()

# Drop All data in tables
def drop_db():
    with app.app_context():
        db.drop_all()

# -------------------------- CRUD OPERATIONS --------------------------
# Create Operation
def create_users():
    with app.app_context():
        new_user = User(username='Yahia2', email='Yahia2@gmail.com', password='123')
        db.session.add(new_user)
        db.session.commit()

def create_posts():
    with app.app_context():
        user = User.query.first()
        post_1 = Post(title='test title 1', content='test content 1', user_id=user.id)
        post_2 = Post(title='test title 2', content='test content 2', user_id=user.id)
        db.session.add(post_1)
        db.session.add(post_2)
        db.session.commit()

# Read Operation
def read_users():
    with app.app_context():
        # -------------- Query First Record --------------
        # user = User.query.first()
        # print(f"user is {user}")
        # print(f"user is {user}")
        # for post in user.posts:
        #     print(f"Post title : {post.title} Content : {post.content}")

        # -------------- Query All Data --------------
        # users = User.query.all()
        # for user in users:
        #     print(user)

        # -------------- Query Filter --------------
        # user = User.query.filter_by(password='123').all()
        # user = User.query.filter_by(password='123').first()
        # print(user)

        # -------------- Join Query --------------
        query = db.session.query(
            Post,
            User
        )\
        .join(User, Post.user_id == User.id)\
        .filter(Post.title == 'test title 1')\
        .all()

        # .order_by(Post.id.desc())\

        for item in query:
            print(item.Post.title)
            print(item.User.username)

# Update Operation
def update_users():
    with app.app_context():
        user = User.query.first()
        print(user)
        user.email = 'asd@gmail.com'
        db.session.commit()
        user = User.query.first()
        print(user)

# Delete Operation
def delete_posts():
    with app.app_context():
        post = Post.query.first()
        print(post)

        db.session.delete(post)
        db.session.commit()
        post = Post.query.first()
        print(post)

# Snippet allows us to run func from within terminal with :
# python db_test.py create_db
if __name__ == '__main__':
    globals()[sys.argv[1]]()