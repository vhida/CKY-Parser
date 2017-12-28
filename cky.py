from pprint import pprint
from node import Node
# The productions rules have to be binarized.

grammar_text = """
S -> NP VP
S -> NP_s VP_s
NP -> Det Noun

VP -> Verb NP
VP -> Verb NP_s
VP_s -> Verb_s NP
VP_s -> Verb_s NP_s
NP_s ->Det Noun_s
PP -> Prep NP
NP -> NP PP
VP -> VP PP
"""
#add VP -> Verb_s NP_s as single form. the original VP -> Verbs NP as plural form

lexicon = {
    'Noun': set(['cats', 'dogs', 'table', 'food']),
    'Noun_s' : set(['cat','dog']),
    'Verb': set(['attacked', 'attack','saw', 'loved', 'hated']),
    'Verb_s':set(['attacks']),
    'Prep': set(['in', 'of', 'on', 'with']),
    'Det': set(['the', 'a']),
}

# Process the grammar rules.  You should not have to change this.
grammar_rules = []
for line in grammar_text.strip().split("\n"):
    if not line.strip(): continue
    left, right = line.split("->")
    left = left.strip()
    children = right.split()
    rule = (left, tuple(children))
    grammar_rules.append(rule)
possible_parents_for_children = {}
for parent, (leftchild, rightchild) in grammar_rules:
    if (leftchild, rightchild) not in possible_parents_for_children:
        possible_parents_for_children[leftchild, rightchild] = []
    possible_parents_for_children[leftchild, rightchild].append(parent)
# Error checking
all_parents = set(x[0] for x in grammar_rules) | set(lexicon.keys())
for par, (leftchild, rightchild) in grammar_rules:
    if leftchild not in all_parents:
        assert False, "Nonterminal %s does not appear as parent of prod rule, nor in lexicon." % leftchild
    if rightchild not in all_parents:
        assert False, "Nonterminal %s does not appear as parent of prod rule, nor in lexicon." % rightchild

# print "Grammar rules in tuple form:"
# pprint(grammar_rules)
# print "Rule parents indexed by children:"
# pprint(possible_parents_for_children)


def cky_acceptance(sentence):
    # return True or False depending whether the sentence is parseable by the grammar.
    global grammar_rules, lexicon

    # Set up the cells data structure.
    # It is intended that the cell indexed by (i,j)
    # refers to the span, in python notation, sentence[i:j],
    # which is start-inclusive, end-exclusive, which means it includes tokens
    # at indexes i, i+1, ... j-1.
    # So sentence[3:4] is the 3rd word, and sentence[3:6] is a 3-length phrase,
    # at indexes 3, 4, and 5.
    # Each cell would then contain a list of possible nonterminal symbols for that span.
    # If you want, feel free to use a totally different data structure.

    backprob = cky_process(sentence)
    return acceptance(backprob)


def cky_process(sentence):
    # Return one of the legal parses for the sentence.
    # If nothing is legal, return None.
    # This will be similar to cky_acceptance(), except with backpointers.
    global grammar_rules, lexicon

    N = len(sentence)
    table = [[[] for i in range(N + 1)] for j in range(N + 1)]
    backprob = [[[] for i in range(N + 1)] for j in range(N + 1)]

    for j in range(1, N + 1):
        # table[j - 1][j] += {A if A -> words[j] \in gram}
        for type in lexicon:
            if sentence[j - 1] in lexicon[type]:
                table[j - 1][j].append(type)
                backprob[j - 1][j].append(
                    Node(type, None, None, sentence[j - 1]))

        # Loop over diagonally in the table and fill in the fields using
        # the rules of the grammar. We check subnodes to find out whether
        # a rule applies or not.
        for i in reversed(range(0, j - 1)):  # (j - 2, 1) goes to 0
            for k in range(i + 1, j):  # goes to j - 1
                # table[i][j] += {A if A -> B C \in gram,
                # 				  B \in table[i][k]
                #				  C \in table[k][j]}
                for rule in grammar_rules:
                    derivation = rule[1]
                    if isinstance(derivation,tuple):
                        B = derivation[0]
                        C = derivation[1]

                            # If A -> B C and B in table[i][k] and C in
                            # table[k][j].
                        if B in table[i][k] and C in table[k][j]:
                            table[i][j].append(rule[0])
                            # print "table[",i,"][",j,"] = ", rule[0]

                            for b in backprob[i][k]:
                               for c in backprob[k][j]:
                                    if b.root == B and  c.root == C:
                                        backprob[i][j].append(Node(rule[0], b, c, None))

    return backprob[0][N]

def cky_parse(sentence):
    backprob = cky_process(sentence)
    if acceptance(backprob):
        return getParseTrees(backprob)

def acceptance(nodes_back):
    check = False
    for node in nodes_back:
        if node.root == 'S':
            check = True
            return True
    return False

def getParseTrees(nodes_back):
    for node in nodes_back:
        if node.root == 'S':
            return parseTree(node)

def parseTree(root):
    rs = []
    if root.status:
        rs.append(root.root)
        rs.append(root.terminal)
        return rs
    left = parseTree(root.left)
    right = parseTree(root.right)

    rs.append(root.root)
    child = []
    child.append(left)
    child.append(right)
    rs.append(child)
    return rs


## some examples of calling these things...
## you probably want to call only one sentence at a time to help debug more easily.

# print cky_acceptance(['the','cat','attacked','the','food'])
# pprint( cky_parse(['the','cat','attacked','the','food']))
# pprint( cky_acceptance(['the','the']))
# pprint( cky_parse(['the','the']))
# print cky_parse(['the','the'])
# print cky_acceptance(['the','cat','attacked','the','food','with','a','dog'])
# # pprint( cky_parse(['the','cat','attacked','the','food','with','a','dog']) )
# print cky_acceptance(['the','cat'])
# pprint ( cky_parse(['the','cat','attacked','the','food']))
# pprint( cky_parse(['the','cat','attacks','the','dog']) )
