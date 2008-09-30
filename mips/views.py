from django.shortcuts import render_to_response
from mips.models import UserProgram, StateInfo
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from mipper.mips import ProgramFactory
from mipper.ops.math import MipsOverflowException
from django.template.loader import render_to_string
import mipsrunner
from google.appengine.api import users
import pickle
import logging
import helpers

def Authenticated(view):
    def f(*args, **kwargs):
        user = users.get_current_user()
        if user:
            return view(user, *args, **kwargs)
        else:
            return login(None)
    return f

def index(request):
    logged_in = users.get_current_user() != None
    return render_to_response("mips/index.html", {'logged_in' : logged_in})

def login(request):
    return render_to_response("mips/login.html",
                              {"login_url": users.create_login_url("/programs/")})

def logout(request):
    return render_to_response("mips/logout.html",
                              {"logout_url": users.create_logout_url("/")})

@Authenticated
def programs(user, request):
    programs = UserProgram.all().filter("user =", user).fetch(10)
    return render_to_response("mips/programs.html", {"programs": programs})

@Authenticated
def details(user, request, name):
    current_program = UserProgram.all().filter("name =", name).filter("user =", user).get()
    return render_to_response("mips/details.html", {'program' : current_program})

@Authenticated
def update(user, request):
    name = request.POST['name']
    current_program = UserProgram.all().filter("name =", name).filter("user =", user).get()
    current_program.code = request.POST['code']
    current_program.put()
    return HttpResponseRedirect(reverse('mips.views.details', kwargs={'name':current_program.name}))

@Authenticated
def add(user, request):
    name = request.POST['name']
    state_info = StateInfo()
    state_info.put()
    new_program = UserProgram(name=name, code="", user=user, state=state_info)
    new_program.put()
    return HttpResponseRedirect(reverse('mips.views.programs'))

@Authenticated
def delete(user, request):
    name = request.POST['name']
    prog = UserProgram.all().filter("name =", name).filter("user =",user).get()
    prog.delete();
    return HttpResponseRedirect(reverse('mips.views.programs'))

@Authenticated
def reset(user, request):
    name = request.POST['name']
    query = UserProgram.all()
    query.filter("name =", name)
    prog = query.filter("user =", user).get()
    return HttpResponseRedirect(reverse('mips.views.details',
                                        kwargs={'name':prog.name}))

@Authenticated
def run(user, request, name):
    query = UserProgram.all()
    query.filter("name =", name)
    query.filter("user =", user)
    prog = query.get()

    result = {}

    if prog.state.suspended:
        logging.info("resuming from suspension")
        state = pickle.loads(prog.state.state_blob)
        output = prog.state.output
        result = mipsrunner.run_with_state(state, output)
    else:
        logging.info("executing program")
        prog_text = mipsrunner.format_user_program(str(prog.code))
        result = mipsrunner.run_program(prog_text, [])

    if not result.get('exception'):
        prog.state.suspended = result['suspended']
        prog.state.state_blob = pickle.dumps(result['state'], 2)
        prog.state.output = result['output']
        prog.state.put()
        prog.put()

        registers = helpers.extract_registers(result['state'])
        output = helpers.format_output(result['output'])
        json_data = render_to_string("mips/details.json",
                                     {'registers' : registers,
                                      'output' : output})
        return HttpResponse(json_data, mimetype="application/javascript")
    else:
        return HttpResponse("{'exception': '%s'}" % result['exception'], mimetype="application/javascript")
