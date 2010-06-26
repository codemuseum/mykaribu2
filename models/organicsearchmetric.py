from google.appengine.ext import db
from user import User

class OrganicSearchMetric(db.Model):
    fb_user_id = db.StringProperty(indexed=True, required=True)
    user = db.ReferenceProperty(User, required=True, indexed=True)
    search_count = db.IntegerProperty(required=True, indexed=True)
    searches = db.TextProperty()
    updated_at = db.DateTimeProperty(auto_now=True)
