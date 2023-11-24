import re
from tabulate import tabulate

def eliminateLeftRecursionAndLeftFactoring(rulesDiction):
    store = {}
    newDict = {}

    for lhs in rulesDiction:
        alphaRules = []
        betaRules = []
        allrhs = rulesDiction[lhs]

        for subrhs in allrhs:
            if subrhs[0] == lhs:
                alphaRules.append(subrhs[1:])
            else:
                betaRules.append(subrhs)

        if len(alphaRules) != 0:
            lhs_ = lhs + "'"
            while (lhs_ in rulesDiction.keys()) or (lhs_ in store.keys()):
                lhs_ += "'"

            for b in range(0, len(betaRules)):
                betaRules[b].append(lhs_)
            rulesDiction[lhs] = betaRules

            for a in range(0, len(alphaRules)):
                alphaRules[a].append(lhs_)
            alphaRules.append(['#'])
            store[lhs_] = alphaRules

    for left in store:
        rulesDiction[left] = store[left]

    for lhs in rulesDiction:
        allrhs = rulesDiction[lhs]
        temp = dict()
        for subrhs in allrhs:
            if subrhs[0] not in list(temp.keys()):
                temp[subrhs[0]] = [subrhs]
            else:
                temp[subrhs[0]].append(subrhs)

        new_rule = []
        tempo_dict = {}

        for term_key in temp:
            allStartingWithTermKey = temp[term_key]

            if len(allStartingWithTermKey) > 1:
                lhs_ = lhs + "'"
                while (lhs_ in rulesDiction.keys()) or (lhs_ in tempo_dict.keys()):
                    lhs_ += "'"

                new_rule.append([term_key, lhs_])
                ex_rules = []
                for g in temp[term_key]:
                    ex_rules.append(g[1:])
                tempo_dict[lhs_] = ex_rules
            else:
                new_rule.append(allStartingWithTermKey[0])

        newDict[lhs] = new_rule

        for key in tempo_dict:
            newDict[key] = tempo_dict[key]

    return newDict

def first(rule):
    global rules, nonterm_userdef, \
        term_userdef, diction, firsts
    if len(rule) != 0 and (rule is not None):
        if rule[0] in term_userdef:
            return rule[0]
        elif rule[0] == '#':
            return '#'

    if len(rule) != 0:
        if rule[0] in list(diction.keys()):
            fres = []
            rhs_rules = diction[rule[0]]
            for itr in rhs_rules:
                indivRes = first(itr)
                if type(indivRes) is list:
                    for i in indivRes:
                        fres.append(i)
                else:
                    fres.append(indivRes)

            if '#' not in fres:
                return fres
            else:
                newList = []
                fres.remove('#')
                if len(rule) > 1:
                    ansNew = first(rule[1:])
                    if ansNew != None:
                        if type(ansNew) is list:
                            newList = fres + ansNew
                        else:
                            newList = fres + [ansNew]
                    else:
                        newList = fres
                    return newList
                fres.append('#')
                return fres


def follow(nt):
    global start_symbol, rules, nonterm_userdef, \
        term_userdef, diction, firsts, follows

    solset = set()
    if nt == start_symbol:
        # return '$'
        solset.add('$')

    for curNT in diction:
        rhs = diction[curNT]
        for subrule in rhs:
            if nt in subrule:
                while nt in subrule:
                    index_nt = subrule.index(nt)
                    subrule = subrule[index_nt + 1:]
                    if len(subrule) != 0:
                        res = first(subrule)
                        if '#' in res:
                            newList = []
                            res.remove('#')
                            ansNew = follow(curNT)
                            if ansNew != None:
                                if type(ansNew) is list:
                                    newList = res + ansNew
                                else:
                                    newList = res + [ansNew]
                            else:
                                newList = res
                            res = newList
                    else:
                        if nt != curNT:
                            res = follow(curNT)

                    if res is not None:
                        if type(res) is list:
                            for g in res:
                                solset.add(g)
                        else:
                            solset.add(res)
    return list(solset)


def computeFirstsAndFollows():
    global rules, nonterm_userdef, term_userdef, diction, firsts, follows

    # Calculate First sets
    for rule in rules:
        k = rule.split("->")
        k[0] = k[0].strip()
        k[1] = k[1].strip()
        rhs = k[1]
        multirhs = rhs.split('|')
        for i in range(len(multirhs)):
            multirhs[i] = multirhs[i].strip()
            multirhs[i] = multirhs[i].split()
        diction[k[0]] = multirhs

    print(f"\nRules: \n")
    for y in diction:
        print(f"{y}->{diction[y]}")
    print(f"\nAfter elimination of left recursion and After left factoring:\n ")
    diction = eliminateLeftRecursionAndLeftFactoring(diction)
    for y in diction:
        print(f"{y}->{diction[y]}")

    for y in list(diction.keys()):
        t = set()
        for sub in diction.get(y):
            res = first(sub)
            if res is not None:
                if type(res) is list:
                    for u in res:
                        t.add(u)
                else:
                    t.add(res)

        firsts[y] = t

    # Calculate Follow sets
    for NT in diction:
        solset = set()
        sol = follow(NT)
        if sol is not None:
            for g in sol:
                solset.add(g)
        follows[NT] = solset


# this is used in syntax analyzer to create parse table


def createParseTable():
    import copy
    global diction, firsts, follows, term_userdef
    print("\nFirsts and Follow Result table\n")

    mx_len_first = 0
    mx_len_fol = 0
    for u in diction:
        k1 = len(str(firsts[u]))
        k2 = len(str(follows[u]))
        if k1 > mx_len_first:
            mx_len_first = k1
        if k2 > mx_len_fol:
            mx_len_fol = k2

    print(f"{{:<{10}}} "
          f"{{:<{mx_len_first + 5}}} "
          f"{{:<{mx_len_fol + 5}}}"
          .format("Non-T", "FIRST", "FOLLOW"))
    for u in diction:
        print(f"{{:<{10}}} "
              f"{{:<{mx_len_first + 5}}} "
              f"{{:<{mx_len_fol + 5}}}"
              .format(u, str(firsts[u]), str(follows[u])))

    ntlist = list(diction.keys())
    terminals = copy.deepcopy(term_userdef)
    terminals.append('$')

    mat = []
    for x in diction:
        row = []
        for y in terminals:
            row.append('')
        mat.append(row)

    grammar_is_LL = True

    for lhs in diction:
        rhs = diction[lhs]
        for y in rhs:
            res = first(y)
            if '#' in res:
                if type(res) == str:
                    firstFollow = []
                    fol_op = follows[lhs]
                    if fol_op is str:
                        firstFollow.append(fol_op)
                    else:
                        for u in fol_op:
                            firstFollow.append(u)
                    res = firstFollow
                else:
                    res.remove('#')
                    res = list(res) + \
                        list(follows[lhs])
            # add rules to table
            ttemp = []
            if type(res) is str:
                ttemp.append(res)
                res = copy.deepcopy(ttemp)
            for c in res:
                xnt = ntlist.index(lhs)
                yt = terminals.index(c)
                if mat[xnt][yt] == '':
                    mat[xnt][yt] = mat[xnt][yt] \
                        + f"{lhs}->{' '.join(y)}"
                else:
                    # if rule already present
                    if f"{lhs}->{y}" in mat[xnt][yt]:
                        continue
                    else:
                        grammar_is_LL = False
                        mat[xnt][yt] = mat[xnt][yt] \
                            + f",{lhs}->{' '.join(y)}"
    print("\nGenerated parsing table:\n")
    frmt = "{:>15}" * len(terminals)
    print(terminals)
    for i in range(len(mat)):
        print([ntlist[i]]+mat[i])
        print("\t")
    return (mat, grammar_is_LL, terminals)

# this function is used to validate input string


def validateStringUsingStackAndParseTable(parsing_table, grammarll1,
                                   table_term_list, input_string,
                                   term_userdef, start_symbol):

    print(f"\nValidate String => {input_string}\n")

    # for more than one entries
    # - in one cell of parsing table
    if grammarll1 == False:
        return f"\nInput String = " \
            f"\"{input_string}\"\n" \
            f"Grammar is not LL(1)"

    # implementing stack buffer

    stack = [start_symbol, '$']
    buffer = []

    # reverse input string store in buffer
    input_string = input_string.split()
    input_string.reverse()
    buffer = ['$'] + input_string
    input_string = buffer

    print("\t\t\tStack\t", "\t\t\t\t\tInput\t\t\t\t", "\t\t\t\tAction")

    while True:
        #end loop if all symbols matched
        if stack == ['$'] and buffer == ['$']:
            print("{:>20} {:>20} {:>20}"
                  .format(' '.join(stack),
                          ' '.join(buffer),
                          "Valid"))
            return "\nValid String!"
        elif stack[0] not in term_userdef:
            # take font of buffer (y) and tos (x)
            x = list(diction.keys()).index(stack[0])
            y = table_term_list.index(buffer[-1])
            if parsing_table[x][y] != '':
                # format table entry received
                entry = parsing_table[x][y]
                print("{:>30} {:>30} {:>25}".
                      format(''.join(stack),
                             ''.join(buffer),
                             f"T[{stack[0]}][{buffer[-1]}]={entry}"))
                lhs_rhs = entry.split("->")
                lhs_rhs[1] = lhs_rhs[1].replace('#', '').strip()
                entryrhs = lhs_rhs[1].split()
                stack = entryrhs + stack[1:]
            else:
                print( f"\nInvalid String! No rule at " \
                    f"Table[{stack[0]}][{buffer[-1]}].")
                print("panic mode recovery dropped ",buffer[-1],"\n")
                buffer = buffer[:-1]

        else:
            # stack top is Terminal
            if stack[0] == buffer[-1]:
                print("{:>30} {:>30} {:>20}"
                      .format(''.join(stack),
                              ''.join(buffer),
                              f"Matched:{stack[0]}"))
                buffer = buffer[:-1]
                stack = stack[1:]
            else:
                print("\nInvalid String! " \
                    "Unmatched terminal symbols\n panic mode recovery dropped ",buffer[-1],"\n")
                buffer = buffer[:-1]


delimiters = [" ", "+", "-", "*", "/", "=", ";",
              "(", ")", "[", "]", "{", "}", "<", ">", "!", "&", "|", "^", "%", "~", "?", ".", ",", "'", "\""]
keywords = ['int', 'main', 'begin', 'end', 'do', 'while', 'return']

kwd_dict = {"int": "t",
            "float": "t",
            "char": "t",
            "long": "t",
            "double": "t",
            "main": "m",
            "begin": "b",
            "end": "d",
            "do": "do",
            "while": "w",
            "return": "r",
            "+": "o",
            "-": "o",
            "*": "o",
            "/": "o",
            "=": "a",
            "expr": "e",
            "exp": "e",
            "n": "id",
            ",": "cm"
            }


def isKeyword(token):
    if token in keywords:
        return True
    return False


def isDelimiter(ch):
    if ch in delimiters:
        return True
    return False


# this is the lexical analyzer which generates tokens from input file
print("------------------------ LEXICAL ANALYZER---------------------------	")
print("Generating tokens")
tokentable_global = []
tokentable_global.append(["Token No", "Lexeme", "Token", "Line No"])
txt = open("question.txt", "r")
tokens = txt.read()
count = 0

tkncount = 0
delimit_flag = 0
program = tokens.split("\n")
for line in program:
    err = 0
    prevct = tkncount
    count = count + 1
    tokentable_local = []
    tokens = line
    tokens = re.findall(r"[A-Za-z0-9_]+|[0-9]+|[(){}]|\S", tokens)
    tokentable = []
    tokentable.append(["Lexeme", "Token"])
    for token in tokens:
        if isDelimiter(token):
            if token in ["{", "}", "(", ")", ";", ","]:
                tkncount += 1
                tokentable.append([token, "Delimiter"])
                tokentable_local.append([tkncount, token, "Delimiter", count])
                if token in [";"]:
                    delimit_flag = 1
            elif token in ["+", "-", "*", "/", "="]:
                if token in ["+", "-", "*", "/"]:
                    tkncount += 1
                    tokentable.append([token, "Arithmetic Operator"])
                    tokentable_local.append(
                        [tkncount, token, "Arithmetic Operator", count])
                elif token in ["="]:
                    tkncount += 1
                    tokentable.append([token, "Assignment Operator"])
                    tokentable_local.append(
                        [tkncount, token, "Assignment Operator", count])
                else:
                    tokentable.append(
                        [token, "Invalid Character [Error]"])
                    print("Error Recovery: Line Ignored")
                    err = 1
                    break
                    continue
            else:
                if delimit_flag == 1:
                    tokentable.append([token, "Invalid Character [Error]"])
                    print("Error Recovery: Character Ignored")
                    break
        elif isKeyword(token):
            tkncount += 1
            tokentable.append([token, "Keyword"])
            tokentable_local.append([tkncount, token, "Keyword", count])
        else:
            if token.isnumeric():
                tkncount += 1
                tokentable.append([token, "Number"])
                tokentable_local.append([tkncount, token, "Number", count])
            else:
                if re.match("^[a-zA-Z][a-zA-Z0-9_]*", token) is not None:
                    tkncount += 1
                    tokentable.append([token, "Identifier"])
                    tokentable_local.append(
                        [tkncount, token, "Identifier", count])
                else:
                    tokentable.append([token, "Invalid Character [Error]"])
                    print("Error Recovery: Line Ignored")
                    err = 1
                    break
            delimit_flag = 0
    if err != 1:
        for entry in tokentable_local:
            tokentable_global.append(entry)
    else:
        tkncount = prevct
print("\nGlobal Token Table: ")
for i in tokentable_global:
    print(i[1],"\t\t",i[2],"\t\t",i[3])
mth_flag = 0
# For the parser tool mth_flag=0 with open('tokens.txt', 'w') as f: str_to_load=""	for token in tokentable_global[1:]:
mth_flag = 0
with open('tokens.txt', 'w') as f:
    str_to_load = ""
    for token in tokentable_global[1:]:
        if mth_flag > 0:
            mth_flag -= 1
            continue
        if kwd_dict.get(token[1]) is not None:
            sym = kwd_dict.get(token[1]) 
        elif re.match("^[a-zA-Z][a-zA-Z0-9_]*", token[1]):
            sym = "id"
        else:
            sym = token[1]
        str_to_load += str(sym)+" "
        if token[1] == "main":
            mth_flag = 2
    f.write(f"{str_to_load}\n")


sample_input_string = ""
rules = ["S -> A B",
         "A -> t m",
         "B -> b M W r ( id ) d",
         "M -> t ID ; | #",
         "ID -> cm id ID | id ID | #",
         "E1 -> e a e E ;",
         "E -> o e E | #",
         "E2 -> id a e E ;",
         "W -> do ME w ( C ) | #",
         "C -> e E C1",
         "C1 -> a a e E | # ",
         "ME -> E1 ME | E2 ME | #"]
nonterm_userdef = ['S', 'A', 'B', 'M', 'E1', 'E2', 'W', 'ID', 'E', 'ME', 'C', 'C1']
term_userdef = ['t', 'm', 'b', 'd', 'r', 'e', 'o', ';',
                'id', 'a', 'do', 'w', '(', ')','cm']
inps = ''

print("-----------------------Syntax Analysis (Parser)-----------------------")
with open('tokens.txt', 'r+') as f:
    for line in f.readlines():
        inps += line
    sample_input_string = inps
    diction = {}
    firsts = {}
    follows = {}
    start_symbol = "S"
    computeFirstsAndFollows()
    (parsing_table, result, tabTerm) = createParseTable()
    if sample_input_string != None:
        print("-------------------------------Semantic Analysis:----------------------------")
        validity = validateStringUsingStackAndParseTable(
            parsing_table, result, tabTerm, sample_input_string, term_userdef, start_symbol)
        print(validity)
    else:
        print("\nNo input String detected")
