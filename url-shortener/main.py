import os,random,re
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
import logging

class ShortUrl(db.Model):
    ourl = db.StringProperty()
    code=db.StringProperty()
    surl=db.StringProperty()


class MainPage(webapp.RequestHandler):
    def get(self):

	if users.get_current_user():
            ur = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            ur = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        user=users.get_current_user()
          
        template_values = { 'ref' : self.request.get('url'),
                    'slug': self.request.get('slug'), 'ur': ur, 'url_linktext':url_linktext,'user':user }


        path = os.path.join(os.path.dirname(__file__), 'index.html')
	self.response.out.write(template.render(path, template_values))

    def handle_error(self, msg):
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, { 'error' : msg,
            'slug': self.request.get('slug'), 'ref': self.request.get('url'),
        }))

    def post(self):
	try:
	    s=1
	    z=0
	    count=[]
	    ourl = self.request.get('url')
	    code=self.request.get('slug')
            char_array = "abcdefgijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-_"
            notes= db.GqlQuery("SELECT * FROM ShortUrl WHERE  ourl= :1",ourl)
     	    count=notes.fetch(1)
	    oslug=db.GqlQuery("SELECT * FROM ShortUrl WHERE  code= :1",code)
     	    cnt=oslug.fetch(1)
	    z=len(count)
	    y=len(cnt)
	    if z > 0:
	        surl=count[0].surl
 	    if code:
	        if y >0:
	            raise SlugException("""
                    The customized url you specified (%s) <b>has already been taken</b>.
                    Try using a different url or leave it blank for a default.
                    """ % code)
	        elif y==0:
		    surl="http://url-shortner.appspot.com/"+code
		    data=ShortUrl()
		    data.ourl=ourl
		    data.code=code
		    data.surl=surl
		    data.put()

            elif z==0:
	        while s>0:
	            word = "".join(random.choice(char_array) for i in range(4))
                    x = db.GqlQuery("SELECT * FROM ShortUrl WHERE code=:1",word)
                    count = x.fetch(1)
                    s = len(count)   		
	        surl="http://url-shortner.appspot.com/"+word
	        data=ShortUrl()
	        data.ourl=ourl
	        data.code=word
	        data.surl=surl
	        data.put()
	    template_values = {'ref' : ourl,
                'ShortUrl' : ourl,
                'short_url': surl.replace("www.", ""), } 
            path = os.path.join(os.path.dirname(__file__), 'index.html')
            self.response.out.write(template.render(path, template_values))
	except SlugException, slug_error:
            return self.handle_error(str(slug_error))
	except Exception, ex:
            msg = """The URL you submitted (%s) does not appear to be a valid one !
             <br/>%s.
             """ % (self.request.get('url'), str(ex))
            return self.handle_error(msg)

	 
class SlugException(Exception):
        def __init__(self, value = ''):
            self.value = value
        def __str__(self):
            return self.value


class ForwardUrl(webapp.RequestHandler):
    def handle_error(self, msg):
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, { 'error' : msg,
            'slug': self.request.get('slug'), 'ref': self.request.get('url'),
        }))
    def get(self,path):
	try:
	    code = self.request.path[1:]
            x = ShortUrl.all()
            x = db.GqlQuery("SELECT * FROM ShortUrl WHERE code= :1",path)
            count = x.fetch(1)
	    y=len(count)
            if y==1:
                ourl = count[0].ourl
                self.redirect(ourl)
	    else:
		raise SlugException("""
                    The code you specified (%s) does not exists in the database !
                    """ % code)
	except SlugException, slug_error:
            return self.handle_error(str(slug_error))




def main():
  application = webapp.WSGIApplication([('/', MainPage),('/(.+)',ForwardUrl)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
