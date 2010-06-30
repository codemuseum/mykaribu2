#!/usr/bin/env python
from google.appengine.ext import webapp
from google.appengine.ext import db
from django.utils import simplejson
import datetime
import facebook
import logging

# *** Helpers
import helpers as h

# *** Models
from models.user import User
from models.usergraph import UserGraph

# Admin main handler
class FetchUserGraphHandler(webapp.RequestHandler):
    def get(self):
        user = User.gql("WHERE __key__ = :1", db.Key(self.request.get('key'))).get()
        if user == None:
            logging.error("Reparse User Graph request couldn't find user by key:%s", self.request.get('key'))
            return False
          
        user_graph = UserGraph.gql("WHERE user = :1", user).get()
        if user_graph == None:
            user_graph = UserGraph(user = user, fb_user_id = user.fb_user_id)
        else:
            user_graph.fb_user_id = user.fb_user_id
        
        # TODO: Not sure if this access token is the most recent.
        graph = facebook.GraphAPI(user.fb_oauth_access_token)
        me = graph.get_object("me")
        user_graph.me = simplejson.dumps(me)
        user_graph.updated_me_at = datetime.datetime.utcnow()
        
        likes = graph.get_connections("me", "likes")
        user_graph.likes = simplejson.dumps(likes)
        user_graph.updated_likes_at = datetime.datetime.utcnow()
        
        user_graph.put()
        
        
        self.response.out.write(simplejson.dumps({'status': 'ok'}))
        