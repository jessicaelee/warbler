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

        # db.create_all()

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        password = 'HASHED_PASSWORD'

        # self.client = app.test_client()

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

    # def tearDown(self):
    #     db.session.remove()

        # db.drop_all()

    def test_list_users(self):
        """Are all users shown when blank search"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2.id

            resp = c.get('/users')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.u1.username, html)
            print(dir(self))
            self.assertIn(self.u2.username, html)
            self.assertIn(self.u3.username, html)

    def test_user_details(self):
        """test view of user details"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            resp = c.get(f'/users/{self.u1.id}')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'@{self.u1.username}</h4>', html)
            self.assertNotIn(f'@{self.u2.username}</h4>', html)
            self.assertNotIn(f'@{self.u3.username}</h4>', html)