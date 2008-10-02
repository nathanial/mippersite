from mipper.mips import ProgramFactory, Program, IO
from mipper.ops.math import MipsOverflowException
import sys
from helpers import format_exception

def std_out(val): pass

def std_in():
    return "blah"


suspended = False

def notify_suspend(state):
    global suspended
    suspended = True


std_factory = ProgramFactory(input = std_in,
                             output = std_out,
                             on_suspension = std_out)

def format_user_program(text):
    prog_text = ""
    for line in text.splitlines():
        prog_text += line.replace('\"', '"').replace('\\n', '\n') + "\n"

    return prog_text

class ErrorCatcher:
    def __init__(self):
        self.error_buf = []
    def write(self, val):
        self.error_buf.append(str(val))

def run_program(prog_text, output_buf):
    def to_buf(val):
        output_buf.append(str(val))
    error_catcher = ErrorCatcher()
    config = dict(text = prog_text,
                  output = to_buf,
                  on_suspension = notify_suspend)

    old_err = sys.stderr
    try:
        sys.stderr = error_catcher
        executable = std_factory.create_program(**config)
        sys.stderr = old_err
    except:
        e = sys.exc_info()[1]
        exception, msg_list = format_exception(e, error_catcher.error_buf)
        return dict(exception = exception, msg_list = msg_list)
    else:
        return execute(executable, output_buf)

def run_with_state(state, output_buf):
    def to_buf(val):
        output_buf.append(str(val))

    config = dict(state = state,
                  on_suspension = notify_suspend,
                  io = IO(input = std_in,
                          output = to_buf))
    executable = Program(**config)
    return execute(executable, output_buf)

def execute(executable, output_buf):
    global suspended
    suspended = False
    try:
        executable.execute()
    except MipsOverflowException:
        return dict(exception = "MipsOverflow", msg_list = "[]")
    except:
        return dict(exception = "Error", msg_list = "[]")

    result = dict(suspended = suspended,
                  state = executable.state,
                  output = output_buf)
    return result

