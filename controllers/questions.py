from google.appengine.ext import webapp, blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import urlfetch
from django.utils import simplejson
from google.appengine.ext import db

from models.question import Question
from models.answer import Answer

import helpers as h
import urllib
import logging


class QuestionsHandler(webapp.RequestHandler):
    def get(self):
        c = h.context()
        s = self.request.get('s')
        c['s'] = s
        c['data'] = xrange(6)
        r = list()
        r += [[0,0]]
        r += [[253,0]]
        r += [[506,0]]
        r += [[0,253]]
        r += [[253,253]]
        r += [[506,253]]
        c['rects'] = r
        c['stash_items'] = xrange(7)
        cookies = h.get_default_cookies(self)
        u = h.get_current_user(cookies)
        if u:
            c['uid'] = u.fb_user_id

        # get some appropriate questions
        query = Question.all()
        query.filter("qtype =", 1).filter("status =", 1)
        questions = query.fetch(1000)
        building = list()
        for o in questions:
            d = dict()
            #d['qtype'] = o.qtype
            d['key'] = str(o.key())
            d['qtext'] = o.qtext
            d['hint'] = o.hint
            d['img'] = str(o.img.key())
            #d['status'] = o.status
            #d['created_at'] = str(o.created_at)
            building += [d]
        c['questions'] = simplejson.dumps(building)

        answers = self.get_answers()
        building = list()
        for o in answers:
            d = dict()
            d['key'] = str(o.key())
            d['atext'] = o.atext
            d['qkey'] = str(o.qkey)
            building += [d]
        c['answers'] = simplejson.dumps(building)

        h.render_out(self, 'questions.tplt', c)

    def get_answers(self):
        query = Answer.all()
        cookies = h.get_default_cookies(self)
        current_user = h.get_current_user(cookies)
        query.filter("user =", current_user)
        answers = query.fetch(1000)
        return answers

class AnswerRecorderHandler(webapp.RequestHandler):
    def get(self):
        c = h.context()
        a = self.request.get('a')
        qk = self.request.get('qk')
        self.add_answer(a,qk)
        h.output(self, "ok")
        
    def add_answer(self, atext, qkey):
        answer = Answer()
        cookies = h.get_default_cookies(self)
        current_user = h.get_current_user(cookies)
        if current_user:
            answer.user = current_user
        answer.atext = atext
        answer.qkey = db.Key(qkey)
        answer.put()
        return answer
