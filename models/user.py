from google.appengine.ext import db

class User(db.Model):
    fb_user_id = db.StringProperty(required=True, indexed=True)
    fb_oauth_access_token = db.StringProperty(indexed=True)
    fb_oauth_access_token_stored_at = db.DateTimeProperty()
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    email = db.EmailProperty()
    signup_url = db.StringProperty()
    signup_referrer = db.StringProperty()
    destroyed_at = db.DateTimeProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)
    admin = db.BooleanProperty(required=True, default=False)
