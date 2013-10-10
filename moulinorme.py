#! /usr/bin/env python

import sys
import re

score = 0
curr_file = ''
curr_line = 0
in_func_param = False
in_func = False
func_param_number = 0
func_count = 0
func_line_count = 0

MAX_LEN = 80
MAX_PARAM_NUMBER = 4
MAX_LINES_FUNC = 25
MAX_FUNCS = 5
MAX_PARAM = 4

# utilities ---------------------

def emit_err(msg, malus = 1):
    print('{0}:{1}:\t{2} (-{3} pt(s))'.format(curr_file, curr_line, msg, malus))
    global score
    score -= malus

def regex_test(string, regex):
    p = re.compile(regex)
    return p.match(string)

def check_len(line):
    balen = len(line)

    if balen > MAX_LEN:
        emit_err("line too long", balen - MAX_LEN)

# pure test functions -----------

def c_specifics(line):
    if regex_test(line, '^#[ \t]*define'):
        emit_err('defines aren\'t really allowed within a C file')

def check_trailing(line):
    count = 1

    if len(line) == 0:
        return
    while count <= len(line) and line[-count] == ' ':
        count += 1
    if count > 1:
        emit_err("trailing space(s)", count - 1)

def check_func(line):
    global in_func_param
    global func_line_count
    global func_param_number
    global func_count
    global MAX_PARAM

    if in_func_param:
        if regex_test(line, '{'):
            in_func_param = False
            func_line_count += 1
            func_count += 1
            if func_param_number > MAX_PARAM:
                emit_err("too many parameters", func_param_number - MAX_PARAM)
            func_param_number = 1
            return 0
    if func_line_count == 0:
        if regex_test(line, '^.*\(.*\)$'):
            func_line_count += 1
        if regex_test(line, '^.*\('):
            in_func_param = True
            return 0

    # are we going out ?
    if func_line_count > 0 and regex_test(line, '^}'):
        # +2 because we count the brackets
        if func_line_count - 2 > MAX_LINES_FUNC:
            emit_err('function is is more than {} lines'.format(MAX_LINES_FUNC), (func_line_count - 2) - MAX_LINES_FUNC)
            func_line_count = 0
            return 0
    if func_line_count > 0:
        func_line_count += 1



def check_file(file):
    global curr_file
    global curr_line
    global in_func_param
    global in_func
    global func_count
    global func_line_count
    global func_param_number

    curr_file = file
    curr_line = 0
    in_funcs_params = False
    in_func = False
    func_count = 0
    func_line_count = 0
    func_param_number = 0

    with open(file) as f:
        line = f.readline()
        while line:
            line = line.replace('\n', '')
            curr_line += 1
            check_len(line)
            check_trailing(line)
            if file.endswith('.c'):
                c_specifics(line)
                check_func(line)
            line = f.readline()

if __name__ == '__main__':

    for file in sys.argv[1:]:
        check_file(file)
    print('note finale : {}'.format(score))
