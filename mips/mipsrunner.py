from mipper.mips import ProgramFactory, Program, IO
from mipper.ops.math import MipsOverflowException

def std_out(val):
    print val,

def std_in():
    return "blah"

def just_print(state):
    print state


suspended = False

def notify_suspend(state):
    print "calling notify suspend"
    global suspended
    suspended = True


std_factory = ProgramFactory(input = std_in,
                             output = std_out,
                             on_suspension = just_print)

def format_user_program(text):
    prog_text = ""
    for line in text.splitlines():
        prog_text += line.replace('\"', '"').replace('\\n', '\n') + "\n"

    return prog_text

def run_program(prog_text, output_buf):
    def to_buf(val):
        output_buf.append(val)

    executable = std_factory.create_program(prog_text,
                                            output = to_buf,
                                            on_suspension = notify_suspend)
    return execute(executable, output_buf)

def run_with_state(state, output_buf):
    def to_buf(val):
        output_buf.append(val)

    executable = Program(state = state, on_suspension = notify_suspend,
                         io = IO(input = std_in,
                                 output = to_buf))
    return execute(executable, output_buf)

def execute(executable, output_buf):
    global suspended
    suspended = False
    try:
        executable.execute()
    except MipsOverflowException:
        return dict(exception = "MipsOverflow", mimetype="application/javascript")

    print "value of suspend = %s" % str(suspended)
    result = dict(suspended = suspended,
                  state = executable.state,
                  output = output_buf)
    return result

