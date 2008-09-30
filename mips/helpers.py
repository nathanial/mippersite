import re

def extract_registers(state):
    non_numerical_key = re.compile(r"\$[a-z].*")
    registers = []
    for k,v in state.registers.items():
        if non_numerical_key.match(k):
            registers.append({'name': str(k), 'value': str(v)})

    return registers

def format_output(output):
    return "".join(map(lambda x : str(x), output)).splitlines()
