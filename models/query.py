from google.appengine.ext import db
from user import User

class Query(db.Model):
    fb_user_id = db.StringProperty(indexed=True)
    user = db.ReferenceProperty(User)
    fb_wall_post_id = db.StringProperty(indexed=True)
    query_string = db.StringProperty(indexed=True, required=True)
    referrer = db.TextProperty()
    url = db.TextProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)
    
    