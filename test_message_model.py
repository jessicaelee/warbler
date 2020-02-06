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


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):

        db.session.rollback()

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User.signup(
            email="test1@test.com",
            username="testuser1",
            password='hashedpw',
            image_url=None
            )

        text = 'This is a message'

        message1 = Message(text=text)

        u1.messages.append(message1)

        db.session.add_all([u1, message1])
        db.session.commit()

        self.u1 = u1

    def test_message_created(self):
        """Test to make sure message is created from setup and new message"""

        message2 = Message(text='another one')
        self.u1.messages.append(message2)
        db.session.add(message2)
        db.session.commit()

        self.assertEqual(Message.query.count(), 2)

    def test_messages_deleted_when_user_deleted(self):
        """test that messages will be deleted when user is deleted"""

        db.session.delete(self.u1)
        db.session.commit()

        self.assertEqual(Message.query.count(), 0)       
