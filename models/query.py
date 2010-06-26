from google.appengine.ext import db
from user import User

class Query(db.Model):
    fb_user_id = db.StringProperty(indexed=True)
    user = db.ReferenceProperty(User, indexed=True)
    fb_wall_post_id = db.StringProperty(indexed=True)
    query_string = db.StringProperty(indexed=True, required=True)
    referrer = db.TextProperty()
    url = db.TextProperty()
    session_id = db.StringProperty(indexed=True)
    ip_address = db.StringProperty(indexed=True)
    created_at = db.DateTimeProperty(auto_now_add=True, indexed=True)
    
    