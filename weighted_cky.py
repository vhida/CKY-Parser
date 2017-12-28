from pprint import pprint
from collections import defaultdict
from p_node import PNode

import sys
from random import choice


grammar_rules = []
lexicon = {}
probabilities = {}
possible_parents_for_children = {}


def populate_grammar_rules():
    global grammar_rules, lexicon, probabilities, possible_parents_for_children
    # TODO Fill in your implementation for processing the grammar rules.

    with open("pcfg_grammar_modified",'r') as file:
        for line in file:
            left,right = line.strip(' ').strip('\n').split('->')
            left = left.strip()
            items = right.strip().split()
            if len(items) == 3 : # binary rules
                grammar_rules.append((left,(items[0],items[1]))) # tuple (rule, (left, right), prob)
                probabilities[(left,(items[0],items[1]))] = float(items[2])

            if len(items) == 2:
                if items[0][0].islower() : #lexicon
                    if left not in lexicon:
                        lexicon[left] = []
                    lexicon[left].append(items[0])
                    probabilities[(left,items[0])] = float(items[1])
                else:
                    grammar_rules.append((left, (items[0]))) # unary rule
                    probabilities[(left, (items[0]))] = float(items[1])

    print("Grammar rules in tuple form:")
    pprint(grammar_rules)
    # print "Rule parents indexed by children:"
    # pprint(possible_parents_for_children)
    print("probabilities")
    pprint(probabilities)
    print("Lexicon")
    pprint(lexicon)


def Dict(**args):
    """Return a dictionary with argument names as the keys,
    and argument values as the key values"""
    return args


# The grammar
# A line like:
#    NP = [['Det', 'N'], ['N'], ['N', 'PP'],
# means
#    NP -> Det N
#    NP -> N
#    NP -> N PP
grammar = Dict(
    S={('NP', 'VP'): .8, ('Aux_NP', 'VP'): .1, ('VP'): .1},
    Aux_NP={('Aux', 'Np'): 1},
    NP ={('Pronoun'):0.2,('ProperNoun'):0.2,('Det','Nominal'):0.6},
    Nominal={('Noun'):0.3,('Nominal','Noun'):0.2,('Nominal','PP'):0.5},
    VP = {('Verb'):0.2,('Verb','NP'):0.5,('VP','PP'):0.3},
    PP = {('Prep','NP'): 1},
    Det = {'the':0.6,'a':0.2,'that':0.1,'this':0.1},
    Noun = {'book':.1,'flight':0.5,'meal':0.2,'money':0.2},
    Verb = {'book':.5,'include':.2,'prefer':.3},
    Pronoun = {'i':.5,'he':.1,'she':.1,'me':.3},
    ProperNoun = {'houston':.8,'nwa':.2},
    Aux = {'does':1},
    Prep = {'from':.25,'to':.25,'on':.1,'near':.2,'through':.2}
    )


def generate_tree(phrase):
    """Generate a random sentence or phrase,
     with a complete parse tree."""
    if isinstance(phrase, list):
        return map(generate_tree, phrase)
    elif phrase in grammar:
        return [phrase] + generate_tree(choice(grammar[phrase]))
    else:
        return [phrase]


def mappend(fn, list):
    "Append the results of calling fn on each element of list."
    return reduce(lambda x, y: x + y, map(fn, list))


def producers(constituent):
    # print constituent
    "Argument is a list containing the rhs of some rule; return all possible lhs's"
    results = []
    for (lhs, rhss) in grammar.items():
        for rhs in rhss:
            if rhs == constituent:
                results.append(lhs)

    return results


def pcky_parse(sentence):
    "The CYK parser.  Return True if sentence is in the grammar; False otherwise"
    global grammar
    # Create the table; index j for rows, i for columns
    length = len(sentence)
    table = [None] * (length)
    table2 = defaultdict(float)
    trace = {}

    for j in range(length):
        table[j] = [None] * (length + 1)
        for i in range(length + 1):
            table[j][i] = []
    # Fill the diagonal of the table with the parts-of-speech of the words
    for k in range(1, length + 1):
        results = producers(sentence[k - 1].lower())
        for item in results:
            list = (item, sentence[k - 1])
            prob = grammar[item][sentence[k - 1].lower()]
            # print grammar[item][sentence[k-1]]
            table2[k - 1, k, item] = prob
            added = True
            while added:
                added = False
                res  = producers(item)
                for A in res:
                    prob = grammar[A][item] * table2[k-1,k,item]
                    if prob > table2[k-1,k,A]:
                        table2[k - 1, k, A] = prob
                        trace[k-1,k,A] = item
                        added = True
                table[k-1][k].extend(res)
        table[k - 1][k].extend(results)


    # Weighted CYK
    for width in range(2, length + 1):
        for start in range(0, length + 1 - width):
            end = start + width
            for mid in range(start, end):
                max_score = 0
                args = None
                for x in table[start][mid]:
                    for y in table[mid][end]:
                        # print x,y
                        results = producers((x, y))
                        for item in results:
                            prob1 = grammar[item][(x, y)]
                            prob2 = prob1 * table2[start, mid, x] * table2[mid, end, y]
                            checkme = start, end, item
                            if checkme in table2:
                                if prob2 > table2[start, end, item]:
                                    table2[start, end, item] = prob2
                            else:
                                table2[start, end, item] = prob2
                            args2 = x, y, mid
                            if args2 in trace:
                                if prob2 > table2[start, end, item]:
                                    args = x, y, mid
                                    trace[start, end, item] = args
                            else:
                                args = x, y, mid
                                trace[start, end, item] = args
                            trace[start, end, item] = args
                            if item not in table[start][end]:
                                table[start][end].append(item)
            added = True
            while added :
                added = False
                for rule in grammar.items():
                    key = rule[0]
                    val_dict = rule[1]
                    for item in val_dict.keys():
                        if not isinstance(item,tuple):
                            prob = val_dict[item]*table2[start, end, item]
                            if prob > table2[start, end, key]:
                                table2[start, end, key] = prob
                                added = True
                                table[start][end].append(key)
                                trace[start, end, key] = item

    if table2[0, length , 'S']:
        return get_tree(sentence, table2,trace, 0, length, 'S')
    else :
        return None


def get_tree(x, table2,trace, i, j, X):
    n = j - i
    if n == 1:
        return [X, x[i]]
    else:
        rs = []
        rs.append((X,table2[i,j,X]))
        if isinstance(trace[i,j,X],tuple):
            Y, Z, s = trace[i, j, X]

            left =  (get_tree(x, table2,trace, i, s, Y),table2[i,s,Y])
            right = (get_tree(x, table2,trace, s, j, Z),table2[s,j,Z])
            rs.append([left,right])
        else:
            Y = trace[i,j,X]
            left = (get_tree(x, table2,trace, i, j, Y),table2[i,j,Y])
            rs.append([left])
        return rs

