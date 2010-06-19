#!/usr/bin/env python

from google.appengine.ext.webapp import template
from models.user import User
from google.appengine.ext import db
from cookies import Cookies
import logging

cfg = None # holds variables for config of fb app, etc.

# Gets cookies object, set to the default max_age for this application
def get_default_cookies(handler):
    return Cookies(handler,max_age=3600) # Match Facebook Auth Token Expiry 

# If not logged in: Stores page in cookie for after-authentication returning, outputs a page that redirects to top, and returns false.
# Else: returns current_user
def login_required(handler):
    cookies = get_default_cookies(handler)
    cookied_user = get_current_user(cookies)
    if cookied_user == None:
        if handler.request.url.find('/auth2') == -1:
            cookies['post_auth_url'] = handler.request.url
        else:
            logging.warning("OH NO!  handler.request.url had /auth2: == "+handler.request.url)
        c = context()
        c['top_redirect_url'] = ('https://graph.facebook.com/oauth/authorize?'
                         +'type=user_agent&display=page&client_id='
                         +cfg['app_id']+'&redirect_uri='
                         +cfg['fb_url']
                         +'/auth2&scope=publish_stream')
        render_out(handler, "redirector.tplt", c)
        return None
    else:
        return cookied_user    


# Returns current_user if any, or None
def login_optional(handler):
    return get_current_user(get_default_cookies(handler))
    
    
# Returns None if no current user
def get_current_user(cookies):
    if 'uk' in cookies and 'oat' in cookies:
        return User.gql("WHERE __key__ = :1 AND fb_oauth_access_token = :2", db.Key(cookies['uk']), cookies['oat']).get()
    return None

def set_current_user(cookies, user):
    cookies['uk'] = str(user.key())
    cookies['oat'] = user.fb_oauth_access_token

def clear_current_user(cookies):
    del cookies['uk']
    del cookies['oat']

def render_out(handler, filename, c):
    return handler.response.out.write(template.render('templates/'+filename, c))

def output(handler, data):
    return handler.response.out.write(data)

def context():
    c = dict()
    c['cfg'] = cfg
    return c

#def cfg():
#    return cfg;

def init():
    # load general config
    import yaml
    global cfg
    cfg = yaml.load(file('config.yaml','r'))
    # add direct_url dynamically
    import os
    cfg['direct_url'] = "http://"+os.environ['HTTP_HOST']
    cfg['is_deployed'] = (os.environ['SERVER_SOFTWARE'] != "Development/1.0")
    
    # load local config and override general options
    try:
        if cfg['is_deployed']:
            local_config = yaml.load(file('remote_dev.yaml','r'))
        else:
            local_config = yaml.load(file('local.yaml','r'))
    except IOError:
        pass
    else:
        for x in local_config:
            cfg[x] = local_config[x]
    for x in cfg:
        cfg[x] = str(cfg[x])
