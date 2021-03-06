import os

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_

from forms import UserAddForm, LoginForm, MessageForm, UserUpdateForm
from models import db, connect_db, User, Message, Follows, Like

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///warbler'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


#############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

# HELPER FUNCTIONS


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

# ROUTE FUNCTIONS


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    # session.pop(CURR_USER_KEY, None)
    flash('You have successfully logged out.')
    return redirect('/signup')


##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    messages = (Message
                .query
                .filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all())
    
    print("****User.messages.timestamp")

    likes = g.user.liked_messages

    return render_template('users/show.html', g_user=g.user, user=user, messages=messages, likes=likes)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    # referer = request.headers.get("Referer")
    try:
        followed_user = User.query.get_or_404(follow_id)
        g.user.following.append(followed_user)
        db.session.commit()
    except:
        return jsonify(error="error in database. unable to update following status.")
    
    return jsonify(dbupdate=True)

    # return redirect(referer)


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    # referer = request.headers.get("Referer")
    try:
        followed_user = User.query.get(follow_id)
        g.user.following.remove(followed_user)
        db.session.commit()
    except:
        return jsonify(error="error in database. unable to update following status.")

    return jsonify(dbupdate=True)

    # return redirect(referer)  # old version: /users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    # user = User.query.get(session[CURR_USER_KEY])

    form = UserUpdateForm(obj=g.user)

    if form.validate_on_submit():
        user = User.authenticate(g.user.username, form.password.data)
        if user:
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data
            user.header_image_url = form.header_image_url.data
            user.bio = form.bio.data
            user.location = form.location.data

            db.session.commit()
            return redirect(f'/users/{user.id}')
        else:
            flash('Wrong password!')
            return redirect('/')

    return render_template('/users/edit.html', form=form)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


@app.route('/users/<int:user_id>/likes')
def show_likes(user_id):
    """Show all the likes messages of a user"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    likes = g.user.liked_messages

    user = User.query.get_or_404(user_id)
    return render_template('users/likes.html', user=user, likes=likes)

@app.route('/users/<int:user_id>/likes_count')
def return_like_count(user_id):
    """get the number of likes for a user"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    user = User.query.get(user_id)
    if user:
        count = len(user.liked_messages)
        return jsonify(count=count)
    else:
        return jsonify(error="No user found")

@app.route('/users/<int:user_id>/following_count')
def return_following_count(user_id):
    """get the number of following for user"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    user = User.query.get(user_id)
    if user:
        count = len(user.following)
        return jsonify(count=count)
    else:
        return jsonify(error="No user found")

@app.route('/users/<int:user_id>/followers_count')
def return_followers_count(user_id):
    """get the number of followers for user"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    user = User.query.get(user_id)
    if user:
        count = len(user.followers)
        return jsonify(count=count)
    else:
        return jsonify(error="No user found")

##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""
    msg = Message.query.get(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get(message_id)
    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")

@app.route('/messages/<int:message_id>/like', methods=['POST'])
def message_like(message_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    try: 
        message = Message.query.get(message_id)
        if message in g.user.liked_messages:
            Like.query.filter(and_(Like.user_id == g.user.id,
                                Like.message_id == message_id)).delete()
        else:
            like = Like(user_id=g.user.id, message_id=message_id)
            db.session.add(like)

        db.session.commit()
    except: 
        return jsonify(dbupdate=False)
    

    return jsonify(dbupdate=True)

    # referer = request.headers.get("Referer")

    # return redirect(referer)


# @app.route('/messages/<int:message_id>/unlike', methods=['POST'])
# def message_unlike(message_id):

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     Like.query.filter(and_(Like.user_id == g.user.id,
#                            Like.message_id == message_id)).delete()

#     db.session.commit()

#     referer = request.headers.get("Referer")

#     return redirect(referer)


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """

    if g.user:
        following_ids = [user.id for user in g.user.following] + [g.user.id]
        for user in g.user.following:
            following_ids.append(user.id)
        messages = (Message
                    .query
                    .filter(Message.user_id.in_(following_ids))
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())
        
        likes = g.user.liked_messages

        return render_template('home.html', messages=messages, likes=likes, user=g.user)

    else:
        return render_template('home-anon.html')


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
