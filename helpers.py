#!/usr/bin/env python

from google.appengine.ext.webapp import template

cfg = None # holds variables for config of fb app, etc.

def render_out(handler, filename, c):
    return handler.response.out.write(template.render('templates/'+filename, c))

def context():
    c = dict()
    c['cfg'] = cfg
    return c

def cfg():
    return cfg;

def init():
    # load general config
    import yaml
    global cfg
    cfg = yaml.load(file('config.yaml','r'))
    
    # load local config and override general options
    try:
        local_config = yaml.load(file('local.yaml','r'))
    except IOError:
        pass
    else:
        for x in local_config:
            cfg[x] = local_config[x]
    for x in cfg:
        cfg[x] = str(cfg[x])
