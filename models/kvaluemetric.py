from google.appengine.ext import db

class KValueMetric(db.Model):
    span_in_days = db.IntegerProperty(required=True, indexed=True)
    date = db.DateProperty(required=True, indexed=True)
    viral_signups =  db.IntegerProperty(default=0)
    total_signups =  db.IntegerProperty(default=0)
    updated_at = db.DateTimeProperty(auto_now=True)
