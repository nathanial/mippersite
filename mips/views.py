from django.shortcuts import render_to_response
from gaesite.mips.models import UserProgram
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from Mipper.mipper import ProgramFactory
from Mipper.math_ops import MipsOverflowException
from django.template.loader import render_to_string
import re

def std_out(val):
    print val,

def std_in():
    return "blah"

def just_print(state):
    print state

std_factory = ProgramFactory(input = std_in,
                             output = std_out,
                             on_suspension = just_print)

def index(request):
    programs = UserProgram.objects.all().order_by("name")
    return render_to_response("mips/index.html", {"programs": programs})

def details(request, name):
    current_program = UserProgram.objects.get(name=name)
    request.session['current_program'] = current_program
    return render_to_response("mips/details.html", {"program" : current_program})

def update(request):
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

def run(request):
    current_program = request.session.get('current_program')
    prog_text = ""
    for line in current_program.code.splitlines():
        prog_text += line.replace('\"', '"').replace('\\n', '\n') + "\n"

    output_buf = []
    def output_to_buf(val):
        output_buf.append(val)

    executable = std_factory.create_program(prog_text,
                                            output = output_to_buf)

    try:
        executable.execute()
    except MipsOverflowException:
        return HttpResponse("{exception: 'MipsOverflow'}", mimetype="application/javascript")

    non_numerical_key = re.compile(r"\$[a-z].*")
    registers = []
    for k,v in executable.state.registers.items():
        if non_numerical_key.match(k):
            registers.append({'name': str(k), 'value' : str(v)})

    output = "".join(map(lambda x : str(x), output_buf)).splitlines()
    json_data = render_to_string('mips/details.json', { 'registers' : registers,
                                                        'output' : output })
    print output
    return HttpResponse(json_data, mimetype="application/javascript")


