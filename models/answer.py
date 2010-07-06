#!/usr/bin/env python
from google.appengine.ext import db
from google.appengine.ext import blobstore
from user import User
from question import Question

class Answer(db.Model):
	atext = db.TextProperty()
	qkey = db.ReferenceProperty(Question)
	created_at = db.DateTimeProperty(auto_now_add=True)
	user = db.ReferenceProperty(User)
