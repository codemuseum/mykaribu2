from google.appengine.ext import db
from user import User

class InstallMetric(db.Model):
    fb_user_id = db.StringProperty(indexed=True, required=True)
    user = db.ReferenceProperty(User, required=True, collection_name="installmetric_reference_user_set")
    installed_at = db.DateTimeProperty(indexed=True, required=True)
    updated_at = db.DateTimeProperty(auto_now=True)
    installed_via_ad = db.BooleanProperty(required=True, indexed=True, default=False)
    ad_name = db.StringProperty(indexed=True)
    installed_via_newsfeed = db.BooleanProperty(required=True, indexed=True, default=False)
    referring_user = db.ReferenceProperty(User, indexed=True, collection_name="installmetric_reference_referring_user_set")
    newsfeed_search_term = db.StringProperty(indexed=True)
    newsfeed_verb = db.StringProperty(indexed=True)
    installed_via_unknown = db.BooleanProperty(required=True, indexed=True, default=False)
    