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
            return index(None)
    return f

def index(request):
    logged_in = users.get_current_user() != None
    return render_to_response("mips/index.html",
                              {'logged_in' : logged_in,
                               'login_url' : users.create_login_url("/programs/"),
                               'logout_url' : users.create_logout_url("/")
                               })

@Authenticated
def programs(user, request):
    programs = UserProgram.all().filter("user =", user).fetch(10)
    if not programs:
        state_info = StateInfo()
        state_info.put()
        example = UserProgram(name="example",
                              code=helpers.example_code(),
                              user = user,
                              state_info=state_info)
        example.put()
        programs.append(example)

    exception = request.COOKIES.get('exception')
    if not exception:
        return render_to_response("mips/programs.html",
                                  {"programs": programs,
                                   "logout_url" : users.create_logout_url("/")})
    else:
        response = render_to_response("mips/programs.html",
                                      {"programs": programs,
                                       "exception": exception,
                                       "logout_url" : users.create_logout_url("/")})
        response.delete_cookie('exception')
        return response

@Authenticated
def details(user, request, name):
    current_program = UserProgram.find(user, name)
    return render_to_response("mips/details.html", {'program' : current_program,
                                                    'logout_url' : users.create_logout_url("/")})

@Authenticated
def update(user, request):
    name = request.POST['name']
    current_program = UserProgram.find(user, name)
    current_program.code = request.POST['code']
    current_program.put()
    return HttpResponseRedirect(reverse('mips.views.details', kwargs={'name': current_program.name}))

@Authenticated
def add(user, request):
    name = request.POST['name']
    if not UserProgram.find(user, name):
        state_info = StateInfo()
        state_info.put()
        new_program = UserProgram(name=name,
                                  code="",
                                  user=user,
                                  state_info=state_info)
        new_program.put()
        return HttpResponseRedirect(reverse('mips.views.programs'))
    else:
        msg = "Program with name '%s' already exists" % name
        logging.info("EXCEPTION " + msg)
        response = HttpResponseRedirect(reverse('mips.views.programs'))
        response.set_cookie('exception', msg)
        return response

@Authenticated
def delete(user, request):
    name = request.POST['name']
    prog = UserProgram.find(user, name)
    if prog:
        prog.delete();
        return HttpResponseRedirect(reverse('mips.views.programs'))
    else:
        msg = "Cannot delete program with name '%s'<br /> because it does not exist." % name
        response = HttpResponseRedirect(reverse('mips.views.programs'))
        response.set_cookie('exception', msg)
        return response

@Authenticated
def reset(user, request):
    name = request.POST['name']
    program = UserProgram.find(user, name)
    program.resume()
    program.state_info.put()
    program.put()
    return HttpResponseRedirect(reverse('mips.views.details',
                                        kwargs={'name':program.name}))

@Authenticated
def run(user, request, name):
    program = UserProgram.find(user, name)

    result = {}

    if program.is_suspended():
        logging.info("resuming from suspension")
        state = program.state()
        output = program.output()
        result = mipsrunner.run_with_state(state, output)
    else:
        logging.info("executing program")
        prog_text = mipsrunner.format_user_program(str(program.code))
        result = mipsrunner.run_program(prog_text, [])

    if not result.get('exception'):
        if result['suspended']:
            program.suspend()

        program.set_state(result['state'])
        program.set_output(result['output'])
        program.state_info.put()
        program.put()

        registers = helpers.extract_registers(result['state'])
        output = helpers.format_output(result['output'])
        json_data = render_to_string("mips/details.json",
                                     {'registers' : registers,
                                      'output' : output})
        return HttpResponse(json_data, mimetype="application/javascript")
    else:
        response = "{'exception': '%s', 'msg_list': %s}" % (result['exception'], result['msg_list'])
        return HttpResponse(response, mimetype="application/javascript")
