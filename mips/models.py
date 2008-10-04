from appengine_django.models import BaseModel
from google.appengine.ext import db
import pickle
import re
import helpers


#For ClassMethod Stuff
class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable

class TooManyPrograms:
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class ProgramNotFound:
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class StateInfo(BaseModel):
    state_blob = db.BlobProperty()
    suspended = db.BooleanProperty(default=False)
    output = db.StringListProperty(default=[])

    def load_state(self):
        return pickle.loads(self.state_blob)

    def dump_state(self, state):
        self.state_blob = pickle.dumps(state, 2)

    def load_registers(self):
        state = self.load_state()
        non_numerical_key = re.compile(r"\$[a-z].*")
        registers = []
        for k,v in state.registers.items():
            if non_numerical_key.match(k):
                registers.append({'name': str(k), 'value': str(v)})

        return registers

class UserProgram(BaseModel):
    name = db.StringProperty(required = True)
    code = db.TextProperty()
    user = db.UserProperty(required = True)
    state_info = db.ReferenceProperty(StateInfo)

    def reset(self):
        self.state_info.suspended = False
        self.state_info.state_blob = None
        self.state_info.output = []

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

    def registers(self):
        return self.state_info.load_registers()

    @Callable
    def find(user, name):
        query = UserProgram.all()
        query.filter("name =", name)
        query.filter("user =", user)
        program = query.get()
        return program

    @Callable
    def store(user_program):
        user_program.state_info.put()
        user_program.put()

    @Callable
    def remove(user_program):
        user_program.state_info.delete()
        user_program.delete()

    @Callable
    def fetch_max_for(user):
        query = UserProgram.all().filter("user =", user)
        if query.count() > 10:
            raise TooManyPrograms("Too Many Programs!")
        else:
            return query.fetch(10)

    @Callable
    def example_program_for(user):
        state_info = StateInfo()
        state_info.put()
        example = UserProgram(name="example",
                              code=helpers.example_code(),
                              user=user,
                              state_info=state_info)
        example.put()
        return example

    @Callable
    def create_program(user,name):
        state_info = StateInfo()
        state_info.put()
        program = UserProgram(name=name,
                              code="",
                              user=user,
                              state_info=state_info)
        program.put()
        return program

    def __cmp__(self, other):
        if self.name > other.name:
            return 1
        elif self.name == other.name:
            return 0
        else:
            return -1
