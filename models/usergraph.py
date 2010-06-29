from google.appengine.ext import db
from user import User

# Stores the /me and /me/likes json as text for parsing later on
class UserGraph(db.Model):
    user = db.ReferenceProperty(User, required=True, indexed=True)
    fb_user_id = db.StringProperty(required=True, indexed=True)
    me = db.TextProperty()
    updated_me_at = db.DateTimeProperty(indexed=True)
    likes = db.TextProperty()
    updated_likes_at = db.DateTimeProperty(indexed=True)
    created_at = db.DateTimeProperty(auto_now_add=True)