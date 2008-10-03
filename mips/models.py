from appengine_django.models import BaseModel
from google.appengine.ext import db
import pickle


#For ClassMethod Stuff
class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable

class StateInfo(BaseModel):
    state_blob = db.BlobProperty()
    suspended = db.BooleanProperty(default=False)
    output = db.StringListProperty(default=[])

    def load_state(self):
        return pickle.loads(self.state_blob)

    def dump_state(self, state):
        self.state_blob = pickle.dumps(state, 2)


class UserProgram(BaseModel):
    name = db.StringProperty(required = True)
    code = db.TextProperty()
    user = db.UserProperty(required = True)
    state_info = db.ReferenceProperty(StateInfo)

    def suspend(self):
        self.state_info.suspended = True

    def resume(self):
        self.state_info.suspended = False

    def is_suspended(self):
        return self.state_info.suspended

    def state(self):
        return self.state_info.load_state()

    def set_state(self, state):
        self.state_info.dump_state(state)

    def set_output(self, output):
        self.state_info.output = output

    def output(self):
        return self.state_info.output

    @Callable
    def find(user, name):
        query = UserProgram.all()
        query.filter("name =", name)
        query.filter("user =", user)
        program = query.get()
        return program

    def __cmp__(self, other):
        if self.name > other.name:
            return 1
        elif self.name == other.name:
            return 0
        else:
            return -1


