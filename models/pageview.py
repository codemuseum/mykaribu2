#!/usr/bin/env python
from google.appengine.ext import db
from user import User

class PageView(db.Model):
	url = db.TextProperty()
	normalized_url = db.StringProperty(indexed=True)
	referrer = db.TextProperty()
	session_order = db.IntegerProperty(indexed=True)
	session_id = db.StringProperty(indexed=True)
	ip_address = db.StringProperty(indexed=True)
	created_at = db.DateTimeProperty(auto_now_add=True, indexed=True)
	user = db.ReferenceProperty(User, indexed=True)