#!/usr/bin/env python
from google.appengine.ext import db
from google.appengine.ext import blobstore
from user import User

class Question(db.Model):
	qtext = db.TextProperty()
	hint = db.TextProperty()
	img = blobstore.BlobReferenceProperty()
	status = db.IntegerProperty()
	created_at = db.DateTimeProperty(auto_now_add=True)
	user = db.ReferenceProperty(User)
