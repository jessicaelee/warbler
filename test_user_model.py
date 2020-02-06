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

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.session.rollback()

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        password = 'HASHED_PASSWORD'

        u1 = User.signup(
            email="test1@test.com",
            username="testuser1",
            password=password,
            image_url=None
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password=password
        )

        db.session.add_all([u1, u2])
        db.session.commit()

        self.u1 = u1
        self.u2 = u2
        self.password = password
        # self.id = u1.id
        # self.username = u1.username
        # self.email = u1.email

        self.client = app.test_client()
    
    # def tearDown(self):
    #     """ Rollback any errors """
    #     db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(User.query.count(), 3)
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        """Does User __repr__ work as expected?"""

        # u1 = User.query.get(self.id)

        self.assertEqual(str(self.u1), f"<User #{self.u1.id}: {self.u1.username}, {self.u1.email}>")

    def test_user_is_following(self):
        """Does User method is_following successfully indicate whether u1 is following u2"""
        self.assertEqual(self.u1.is_following(self.u2), False)

        self.u1.following.append(self.u2)

        db.session.commit()

        self.assertEqual(self.u1.is_following(self.u2), True)
        self.assertEqual(self.u2.is_following(self.u1), False)

    def test_user_is_followed_by(self):
        """Does User method is_followed_by indicate appropropiately whether u1 is followed by u2"""
        # Running this with follow-up makes second test also equal false...
        self.assertEqual(self.u2.is_followed_by(self.u1), False)

        self.u2.followers.append(self.u1)

        db.session.commit()

        self.assertEqual(self.u2.is_followed_by(self.u1), True)
    
    def test_bad_user_creation_password(self):
        """Test invalid password given to User creation"""

        with self.assertRaises(ValueError):
            User.signup(
                email="test3@test.com",
                username="testuser3",
                password="",
                image_url=None
                )
        
    def test_bad_user_creation_email_duplicate(self):  
        """Test duplicate email given to User creation"""

        with self.assertRaises(IntegrityError):
            User.signup(
                email="test1@test.com",
                username="testuser3",
                password="123456",
                image_url=None
                )
            db.session.commit()

    def test_bad_user_creation_email_null(self):  
        """Test null email given to User creation"""

        with self.assertRaises(IntegrityError):
            User.signup(
                email=None,
                username="testuser3",
                password="123456",
                image_url=None
                )
            db.session.commit()
    
    def test_bad_user_creation_username_duplicate(self):
        """Test duplicate username given to User creation"""

        with self.assertRaises(IntegrityError):
            User.signup(
                email="test3@test.com",
                username="testuser1",
                password="123456",
                image_url=None
                )
            db.session.commit()
    
    def test_bad_user_creation_username_null(self):
        """Test null username given to User creation"""

        with self.assertRaises(IntegrityError):
            User.signup(
                email="test3@test.com",
                username=None,
                password="123456",
                image_url=None
                )
            db.session.commit()

    def test_create_account_successful(self):
        """Test signup with valid inputs"""

        new_user = User.signup(
                    email="test4@test.com",
                    username="newusername",
                    password="123456",
                    image_url=None
                    )
        db.session.commit()

        self.assertEqual(User.query.count(), 3)


    def test_authentication_of_good_username_and_password(self):
        """test login with correct username and password"""

        user1 = User.authenticate(self.u1.username, self.password)

        self.assertEqual(user1, self.u1)

    def test_authentication_of_bad_username(self):
        """test login with an incorrect username"""

        user1 = User.authenticate('badusername', self.password)

        self.assertFalse(user1)
    
    def test_authentication_of_bad_password(self):
        """test login with an incorrect password"""

        user1 = User.authenticate(self.u1.username, 'badpassword')

        self.assertFalse(user1)       