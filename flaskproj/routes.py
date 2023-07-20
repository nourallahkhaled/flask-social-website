# Import Flask
from flask import render_template, redirect, url_for, flash, request, Blueprint, send_from_directory
from flaskproj import app, db, bcrypt
from flaskproj.forms import RegistrationForm, LoginForm, PostForm, ProfileForm
from flaskproj.models import User, Post,Friend
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort
from sqlalchemy import or_
import os

users = Blueprint(
    'users',
    __name__,
    url_prefix='/users'
)

@app.context_processor
def inject_nav_items():
    nav_items = [
        {'url': '/home', 'name': 'Home'},
    ]
    if current_user.is_authenticated:
        profile_url = url_for('profile', user_id=current_user.id)
        nav_items.append({'url': profile_url, 'name': 'Profile'})
        nav_items.append({'url': '/friend_requests', 'name': 'Friend Requests'})
        nav_items.append({'url': '/logout', 'name': 'Log Out'})
    else:
        nav_items.append({'url': '/login', 'name': 'Login'})
    return {'nav_items': nav_items}


# Homepage Endpoint
@app.route('/home')
@login_required
def home():
    filter_option = request.args.get('filter')  # Get the filter option from the query parameter
    public_posts = Post.query.filter(or_(Post.privacy=='public',Post.privacy=='friends')).all()
    friends = current_user.get_friends()
    accepted_friends = [friend.sender if friend.receiver == current_user else friend.receiver for friend in current_user.friends if friend.status == 'accepted']


    if filter_option == 'friends':  # Filter posts based on the option
        friend_ids = [friend.id for friend in current_user.get_friends()]
        friend_posts = Post.query.filter(Post.user_id.in_(friend_ids)).all()
        posts = friend_posts
    else:
        posts = public_posts
    users = User.query.all()
    return render_template('home.html', posts=posts, users=users, friends=friends,accepted_friends=accepted_friends)

# Register Endpoint
@app.route('/register', methods=['GET','POST'])
def register():
    endpoint_title = 'Register Page'
    form = RegistrationForm()
    if form.validate_on_submit():
        with app.app_context():
            hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(
                username=form.username.data,
                gender=form.gender.data,
                email=form.email.data,
                password=hashed_pw
            )
            db.session.add(new_user)
            db.session.commit()

        flash(f"Registration Successful for {form.username.data}!","success")
        return redirect(url_for('login'))

    return render_template('register.html', data={'title':endpoint_title,'form':form})

# Login Endpoint
@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    endpoint_title = 'Login Page'
    form = LoginForm()
    if form.validate_on_submit():
        with app.app_context():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Login Successful!","success")
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect(url_for('home'))

            else:
                flash("Login Unsuccessful!","danger")
                return redirect(url_for('login'))

    return render_template('login.html', data={'title':endpoint_title,'form':form})

# Logout Endpoint
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ------------------- USER ENDPOINTS -------------------
@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    if current_user.is_authenticated:
        user = User.query.get_or_404(user_id)
        form = PostForm()
        profile_form = ProfileForm(obj=user) 

        # Handle new post submission
        if form.validate_on_submit() and current_user.id == user_id:
            post = Post(title=form.title.data, content=form.content.data, privacy=form.privacy.data, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Post created successfully!', 'success')
            return redirect(url_for('profile', user_id=user_id))

        # Handle post edit submission
        if request.method == 'POST' and 'post_id' in request.form and current_user.id == user_id:
            post_id = int(request.form['post_id'])
            post = Post.query.get_or_404(post_id)
            if post.author == current_user:
                post.title = request.form['title']
                post.content = request.form['content']
                post.privacy = request.form['privacy']
                db.session.commit()
                flash('Post updated successfully!', 'success')
                return redirect(url_for('profile', user_id=user_id))

        # Handle profile edit submission
        if profile_form.validate_on_submit() and current_user.id == user_id:
            user.username = profile_form.username.data
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile', user_id=user_id))

        posts = Post.query.filter_by(author=current_user).all()
        return render_template('profile.html', user=user, posts=posts, form=form, profile_form=profile_form)
    else:
        flash("You need to be logged in to access this page.", "danger")
        return redirect(url_for('login'))

# Upload Profile Picture
@app.route('/profile/upload_picture', methods=['POST'])
@login_required
def upload_picture():
    user_id = current_user.id
    user = User.query.get(user_id)
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        user.profile_picture = filename
        db.session.commit()
        flash('Picture uploaded successfully')
    return redirect(url_for('profile', user_id=user_id))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# DELETE POST
@app.route('/profile/delete_post/<int:post_id>', methods=['GET','POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author:
        abort(403) 
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('profile', user_id=current_user.id))

# friend
# Send friend request route
@app.route('/send_friend_request/<int:user_id>', methods=['POST'])
@login_required
def send_friend_request(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    if current_user.is_friend(user):
        flash('You are already friends with this user', 'info')
        return redirect(url_for('profile', user_id=user.id))
    if current_user == user:
        flash('You cannot add yourself as a friend', 'danger')
        return redirect(url_for('profile', user_id=user.id))
    if current_user.friend_requests_sent.filter_by(friend_id=user.id).first() is not None:
        flash('You have already sent a friend request to this user', 'info')
        return redirect(url_for('profile', user_id=user.id))
    friend_request = Friend(sender=current_user, receiver=user)
    db.session.add(friend_request)
    db.session.commit()
    flash(f'Friend request sent to {user.username}', 'success')
    return redirect(url_for('profile', user_id=user.id))


@app.route('/accept_friend_request/<int:request_id>', methods=['POST'])
@login_required
def accept_friend_request(request_id):
    friend_request = Friend.query.filter_by(id=request_id).first_or_404()
    if friend_request.receiver != current_user:
        abort(403)
    friend_request.status = 'accepted'
    db.session.commit()
    return redirect(url_for('friend_requests'))

@app.route('/decline_friend_request/<int:request_id>', methods=['POST'])
@login_required
def decline_friend_request(request_id):
    friend_request = Friend.query.filter_by(id=request_id).first_or_404()
    if friend_request.receiver != current_user:
        abort(403)
    friend_request.status = 'declined'
    db.session.commit()
    return redirect(url_for('friend_requests'))


@app.route('/friend_requests')
@login_required
def friend_requests():
    friend_requests_received = current_user.friend_requests_received.filter_by(status='pending')
    return render_template('friend_requests.html', friend_requests=friend_requests_received)