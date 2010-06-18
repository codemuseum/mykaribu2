#!/usr/bin/env python
from google.appengine.ext import db
from user import User

class PageView(db.Model):
	url = db.TextProperty()
	normalized_url = db.StringProperty()
	referrer = db.TextProperty()
	session_order = db.IntegerProperty()
	session_id = db.StringProperty()
	ip_address = db.StringProperty()
	created_at = db.DateTimeProperty(auto_now_add=True)
	user = db.ReferenceProperty(User)