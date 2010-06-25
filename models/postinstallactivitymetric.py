from google.appengine.ext import db
from user import User

class PostInstallActivityMetric(db.Model):
    fb_user_id = db.StringProperty(indexed=True, required=True)
    user = db.ReferenceProperty(User, required=True, indexed=True)
    installed_at = db.DateTimeProperty(indexed=True, required=True)
    active_day_1 = db.BooleanProperty(default=False, indexed=True)
    active_day_2 = db.BooleanProperty(default=False, indexed=True)
    active_day_3 = db.BooleanProperty(default=False, indexed=True)
    active_day_4 = db.BooleanProperty(default=False, indexed=True)
    active_day_5 = db.BooleanProperty(default=False, indexed=True)
    active_day_6 = db.BooleanProperty(default=False, indexed=True)
    active_day_7 = db.BooleanProperty(default=False, indexed=True)
    updated_at = db.DateTimeProperty(auto_now=True)
