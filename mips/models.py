from appengine_django.models import BaseModel
from google.appengine.ext import db


class StateInfo(BaseModel):
    state_blob = db.BlobProperty()
    suspended = db.BooleanProperty(default=False)
    output = db.StringListProperty(default=[])

class UserProgram(BaseModel):
    name = db.StringProperty(required = True)
    code = db.TextProperty()
    user = db.UserProperty(required = True)
    state = db.ReferenceProperty(StateInfo)

    def __cmp__(self, other):
        if self.name > other.name:
            return 1
        elif self.name == other.name:
            return 0
        else:
            return -1



