
from google.appengine.ext import ndb


def user_key(id):
    """Constructs a Datastore key for a User entity.
        We use user's email as the key.
        """
    return ndb.Key(User, id)


class User(ndb.Model):
    email = ndb.StringProperty()


class Ticket(ndb.Model):
    id = ndb.StringProperty()
    isvalid = ndb.BooleanProperty(default=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
