import json as json
from collections import OrderedDict
from itertools import count

counter = count()
def correct_id(tree, *args):
    tree['id'] = counter.next()

def add_qtype(tree, *args):
    tree['qtype'] = 'R' if 'options' in tree else 'T'

def skip_values(tree, parent):
    if parent is not None:
        if 'skip' not in parent:
            parent['skip'] = set()
        parent['skip'].add(tree['id'])

def traverse_tree(tree, parent=None, fns=[]):
    for fn in fns: fn(tree, parent)
    if 'children' in tree:
        for child in sorted(tree['children'], key=lambda i: int(i)):
            traverse_tree(tree['children'][child], parent=tree, fns=fns)

def print_tree(tree, *args):
    if 'default' in tree:
        print '%s;%s;%s;%s;%s;%s' % (
            tree['id'], tree['qtype'], tree['question'],
            ','.join(tree['options'] if 'options' in tree else ''),
            ','.join(tree['default']),
            ','.join(map(str, sorted(tree['skip']))) if 'skip' in tree else '')

def format_json(tree):
    return {'number': str(tree['id']),
            'question': tree['question'],
            'qtype': tree['qtype'],
            'options': {o: o for o in tree['options']} if 'options' in tree else {},
            'default': tree['default'][0] if tree['default'] else "",
            'skip': [str(s) for s in sorted(tree['skip'])] if 'skip' in tree else []}

def format_connecting_node(tree):
    return {'number': str(tree['id']),
            'question': tree['question'],
            'qtype': "connecting",
            'skip': [str(s) for s in sorted(tree['skip'])] if 'skip' in tree else []}

def tojson(tree):
    if 'default' in tree:
        yield format_json(tree)
    else:
        yield format_connecting_node(tree)
    if 'children' in tree:
        for child in sorted(tree['children'], key=lambda i: int(i)):
            for node in tojson(tree['children'][child]):
                yield node

if __name__ == '__main__':
    with open("questions-tree.json") as inf:
        data = OrderedDict(json.load(inf).items())
    traverse_tree(data, fns=[correct_id, add_qtype, skip_values])
    # traverse_tree(data, fns=[print_tree])
    questions = list(tojson(data))[2:]
    with open("questions.json", "w") as outfile:
        json.dump(questions, outfile, indent=4)



