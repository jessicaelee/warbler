"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Like
from sqlalchemy.exc import IntegrityError

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserViewsTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        password = 'HASHED_PASSWORD'

        self.u1 = User.signup(
            email="test1@test.com",
            username="testuser1",
            password=password,
            image_url=None
        )
        self.u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password=password,
            image_url=None
        )
        self.u3 = User.signup(
            email="test3@test.com",
            username="testuser3",
            password=password,
            image_url=None
        )

        message1 = Message(text='This is 1 message')
        message2 = Message(text='This is 2 message')
        message3 = Message(text='This is 3 message')

        self.u1.messages.append(message1)
        self.u2.messages.append(message2)
        self.u3.messages.append(message3)

        db.session.add_all([message1, message2, message3])
        db.session.commit()


    def test_list_users(self):
        """Are all users shown when blank search"""
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                u1uname = self.u1.username
                u2uname = self.u2.username
                u3uname = self.u3.username

            resp = c.get('/users')

            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(u1uname, html)
            self.assertIn(u2uname, html)
            self.assertIn(u3uname, html)

    def test_user_details(self):
        """test view of user details"""
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                u1uname = self.u1.username
                u2uname = self.u2.username
                u3uname = self.u3.username

            resp = c.get(f'/users/{self.u1.id}')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'@{u1uname}</h4>', html)
            self.assertNotIn(f'@{u2uname}</h4>', html)
            self.assertNotIn(f'@{u3uname}</h4>', html)

    def test_view_followers(self):
        """test user is a follower"""
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                u1 = self.u1.id
                u2 = self.u2.id
                u3 = self.u3.id

            user1 = User.query.get(u1)
            user2 = User.query.get(u2)
            user3 = User.query.get(u3)

            resp = c.post(f'/users/follow/{user2.id}')

            self.assertEqual(resp.status_code, 302)          
            self.assertIn(user1, user2.followers)
            self.assertNotIn(user1, user3.followers)

    def test_view_following(self):
        """test users following"""
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                u1 = self.u1.id
                u2 = self.u2.id
                u3 = self.u3.id

            user1 = User.query.get(u1)
            user2 = User.query.get(u2)
            user3 = User.query.get(u3)

            user1.following.append(user2)

            db.session.commit()

            resp = c.get(f'/users/{u1}/following')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(user2.username, html)
            self.assertNotIn(user3.username, html)

    def test_update_profile_not_loggedin(self):
        """test updating the profile when not logged in"""
        with app.test_client() as c:

            resp = c.post('/users/profile', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.',html)

    # def test_update_profile_loggedin(self):
    #     """test updating profile when logged in"""
    #     with app.test_client() as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.u1.id
    #             u1 = self.u1.id
        
    #     user1 = User.query.get(u1)

    #     resp = c.post('/users/profile', data={'bio': 'we updated the bio'})

    def test_view_liked_messages(self):
        """show liked messages for user"""
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                u1 = self.u1.id
                u2 = self.u2.id
                u3 = self.u3.id

            user1 = User.query.get(u1)
            user2 = User.query.get(u2)
            user3 = User.query.get(u3)

            user1.liked_messages.append(user2.messages[0])

            resp = c.get(f'/users/{user1.id}/likes')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('This is 2 message',html)