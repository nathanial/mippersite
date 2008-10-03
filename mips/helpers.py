import logging
from google.appengine.api import users

def login_url():
    return users.create_login_url("/programs/")

def logout_url():
    return users.create_logout_url("/")

def format_output(output):
    return "".join(map(lambda x : str(x), output)).splitlines()

def format_exception(ex, error_buf):
    def replace_junk(val):
        return str(val).replace("'","").replace('"','')
    ex_str = replace_junk(ex)
    error_lines = "".join(
        map(lambda x : replace_junk(x),
            error_buf)
        ).splitlines()
    logging.info(str(error_lines).replace("\n",""))
    return ex_str, str(error_lines)

def example_code():
    file = open("example.asm")
    code = ""
    for line in file:
        code += line.replace("\\n", "\n")
    file.close()
    return code
