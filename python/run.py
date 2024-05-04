import sys

from scheme.parser import parse
from scheme.interpreter import seval, create_global_env

with open(sys.argv[1], "r") as f:
    global_env = create_global_env()
    tree = []
    for line in f:
        for parsed in parse(line):
            tree.append(parsed)

    for exp in tree:
        seval(exp, global_env)
