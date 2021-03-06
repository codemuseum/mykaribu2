from google.appengine.ext import db
from user import User
from query import Query

class ResultView(db.Model):
    fb_user_id = db.StringProperty(indexed=True)
    user = db.ReferenceProperty(User)
    query = db.ReferenceProperty(Query)
    fb_wall_post_id = db.StringProperty(indexed=True)
    source = db.StringProperty(indexed=True)
    referrer = db.TextProperty()
    url = db.TextProperty()
    session_id = db.StringProperty(indexed=True)
    ip_address = db.StringProperty(indexed=True)
    image_url = db.StringProperty()
    query_string = db.StringProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)
    
