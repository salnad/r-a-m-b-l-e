#where models will go
from google.appengine.ext import ndb
#import google.appengine.ext.db


class Journal(ndb.Model):
    user = ndb.StringProperty(required=True) #email
    text = ndb.StringProperty(required=True)
    rgb1 = ndb.IntegerProperty(repeated=True)
    rgb2 = ndb.IntegerProperty(repeated=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    sumSeconds = ndb.IntegerProperty()
    month = ndb.IntegerProperty()
    year = ndb.IntegerProperty()

class Person(ndb.Model):
    email = ndb.StringProperty(required=True)
    first_name = ndb.StringProperty(required=True)
    last_name = ndb.StringProperty(required=True)
