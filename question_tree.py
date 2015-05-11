import codecs
from collections import OrderedDict
import json

def line2json(line):
    try:
        number, question, options, default, cross = line.strip().split(';')
    except ValueError:
        raise ValueError(line)
    options = options.split(',')
    jstring = {'question': question,
               'number': number,
               'options': OrderedDict((o, o) for o in sorted(options)) if options[0] != '-' else {},
               'qtype': 'R' if len(options) > 1 else 'T',
               'default': default.split(','),
               'skip': []}
    if cross:
        jstring['skip'] = cross.split(',')
    return jstring

def insert_in_tree(questions, child, depth):
    question = questions[-1]
    if depth == 1:
        if 'children' not in question:
            question['children'] = []
        if 'skip' not in question:
            question['skip'] = []
        question['children'].append(child)
        question['skip'].append(child['number'])
    else:
        insert_in_tree(question['children'], child, depth - 1)

def format_json(node):
    return {key: node[key] for key in ('number', 'qtype', 'question', 'skip', 'default', 'options') if key in node}


def flatten_tree(tree):
    for node in tree:
        yield format_json(node)
        if 'children' in node:
            for child in flatten_tree(node['children']):
                yield child

if __name__ == '__main__':    
    questions = []
    for line in codecs.open("vragenlijst.txt", encoding='utf-8'):
        json_line = line2json(line)
        indentation = line.count('\t')
        if indentation == 0:
            questions.append(json_line)
        else:
            insert_in_tree(questions, json_line, indentation)
    questions = list(flatten_tree(questions))
    with open("questions.json", "w") as out:
        json.dump(questions, out, indent=2)