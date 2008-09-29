from django.shortcuts import render_to_response
from gaesite.mips.models import UserProgram
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from mipper.mips import ProgramFactory
from mipper.ops.math import MipsOverflowException
from django.template.loader import render_to_string
import re
import mipsrunner


def index(request):
    programs = UserProgram.objects.all().order_by("name")
    return render_to_response("mips/index.html", {"programs": programs})

def details(request, name):
    current_program = UserProgram.objects.get(name=name)
    request.session['current_program'] = current_program
    return render_to_response("mips/details.html", {"program" : current_program})

def update(request):
    request.session['suspended'] = False
    current_program = request.session.get('current_program')
    current_program.code = request.POST['code']
    current_program.save()
    return HttpResponseRedirect(reverse('gaesite.mips.views.details', kwargs={'name':current_program.name}))

def add(request):
    name = request.POST['name']
    new_program = UserProgram(name=name, code="")
    new_program.save()
    return HttpResponseRedirect(reverse('gaesite.mips.views.index'))

def delete(request):
    name = request.POST['name']
    prog = UserProgram.objects.get(name=name)
    prog.delete();
    return HttpResponseRedirect(reverse('gaesite.mips.views.index'))

def reset(request):
    current_program = request.session['current_program']
    request.session['suspended'] = False
    return HttpResponseRedirect(reverse('gaesite.mips.views.details', kwargs={'name':current_program.name}))

def run(request):
    current_program = request.session.get('current_program')

    result = None
    if request.session.get('suspended'):
        print "Running from Break"
        state = request.session['state']
        result = mipsrunner.run_with_state(state, request.session['output'])
    else:
        print "Running from Beginning"
        prog_text = mipsrunner.format_user_program(current_program.code)
        result = mipsrunner.run_program(prog_text, [])

    if not result.get('exception'):
        request.session['suspended'] = result['suspended']
        request.session['state'] = result['state']
        request.session['output'] = result['output']

        non_numerical_key = re.compile(r"\$[a-z].*")
        registers = []
        for k,v in result['state'].registers.items():
            if non_numerical_key.match(k):
                registers.append({'name': str(k), 'value' : str(v)})

        output = "".join(map(lambda x : str(x), result['output'])).splitlines()
        json_data = render_to_string('mips/details.json', { 'registers' : registers,
                                                        'output' : output })

        print output
        response = HttpResponse(json_data, mimetype="application/javascript")
        return response
    else:
        print "Exception"
        return HttpResponse("{'exception': '%s'}" % result['exception'], mimetype="application/javascript")

