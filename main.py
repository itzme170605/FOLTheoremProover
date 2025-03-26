import sys
import re
import copy

# ------------------------
# Data Classes
# ------------------------

class Term:
    def __init__(self, name):
        self.name = name

    def is_variable(self):
        return re.fullmatch(r"[a-z][a-zA-Z0-9_]*", self.name) is not None

    def is_constant(self):
        return re.fullmatch(r"[A-Z][a-zA-Z0-9_]*", self.name) is not None

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Term) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

class Function:
    def __init__(self, name, args):
        self.name = name
        self.args = args  # list of Term or Function

    def __repr__(self):
        return f"{self.name}({','.join(map(str, self.args))})"

    def __eq__(self, other):
        return isinstance(other, Function) and self.name == other.name and self.args == other.args

    def __hash__(self):
        return hash((self.name, tuple(self.args)))

class Predicate:
    def __init__(self, name, args, negated=False):
        self.name = name
        self.args = args  # list of Term or Function
        self.negated = negated

    def __repr__(self):
        args_str = ",".join(map(str, self.args))
        if self.args:
            return f"{'!' if self.negated else ''}{self.name}({args_str})"
        else:
            return f"{'!' if self.negated else ''}{self.name}"

    def __eq__(self, other):
        return (self.name == other.name and 
                self.args == other.args and 
                self.negated == other.negated)

    def __hash__(self):
        return hash((self.name, tuple(self.args), self.negated))

class Clause:
    def __init__(self, literals):
        self.literals = literals  # list of Predicate

    def __repr__(self):
        return " | ".join(map(str, self.literals))

    def __eq__(self, other):
        return set(self.literals) == set(other.literals)

    def __hash__(self):
        return hash(frozenset(self.literals))

# ------------------------
# CNF File Parsing
# ------------------------

def parse_term_or_function(token):
    token = token.strip()
    if '(' in token:
        match = re.match(r"(\w+)\((.*)\)", token)
        if not match:
            return Term(token)
        name, args_str = match.groups()
        args = [parse_term_or_function(arg.strip()) for arg in split_args(args_str)]
        return Function(name, args)
    else:
        return Term(token)

def split_args(s):
    args = []
    balance = 0
    current = ''
    for char in s:
        if char == ',' and balance == 0:
            args.append(current)
            current = ''
        else:
            if char == '(':
                balance += 1
            elif char == ')':
                balance -= 1
            current += char
    if current:
        args.append(current)
    return args

def parse_predicate(literal):
    negated = literal.startswith("!")
    if negated:
        literal = literal[1:]
    if "(" not in literal:
        return Predicate(literal, [], negated)
    match = re.match(r"(\w+)\((.*)\)", literal)
    if not match:
        return None
    name, args_str = match.groups()
    args = [parse_term_or_function(arg.strip()) for arg in split_args(args_str)]
    return Predicate(name, args, negated)

def parse_clause(line):
    literals = line.strip().split()
    predicates = []
    for l in literals:
        if l:
            pred = parse_predicate(l)
            if pred:
                predicates.append(pred)
    return Clause(predicates)

def parse_input(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    clauses = []
    read_clauses = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("Clauses:"):
            read_clauses = True
            continue
        if read_clauses:
            clause = parse_clause(line)
            if clause.literals:
                clauses.append(clause)
    return clauses

# ------------------------
# Unification
# ------------------------

def is_variable(x):
    return isinstance(x, Term) and x.is_variable()

def unify(x, y, subst):
    if subst is None:
        return None
    elif x == y:
        return subst
    elif is_variable(x):
        return unify_var(x, y, subst)
    elif is_variable(y):
        return unify_var(y, x, subst)
    elif isinstance(x, Function) and isinstance(y, Function):
        if x.name != y.name or len(x.args) != len(y.args):
            return None
        return unify_lists(x.args, y.args, subst)
    elif isinstance(x, list) and isinstance(y, list):
        return unify_lists(x, y, subst)
    else:
        return None

def unify_var(var, x, subst):
    if var in subst:
        return unify(subst[var], x, subst)
    elif x in subst:
        return unify(var, subst[x], subst)
    elif occurs_check(var, x, subst):
        return None
    else:
        subst = subst.copy()
        subst[var] = x
        return subst

def unify_lists(xs, ys, subst):
    if len(xs) != len(ys):
        return None
    for x, y in zip(xs, ys):
        subst = unify(x, y, subst)
        if subst is None:
            return None
    return subst

def occurs_check(var, x, subst):
    if var == x:
        return True
    elif isinstance(x, Term) and x in subst:
        return occurs_check(var, subst[x], subst)
    elif isinstance(x, Function):
        return any(occurs_check(var, arg, subst) for arg in x.args)
    elif isinstance(x, list):
        return any(occurs_check(var, t, subst) for t in x)
    return False

# ------------------------
# Substitution
# ------------------------

def substitute(term, subst):
    if term in subst:
        return substitute(subst[term], subst)
    elif isinstance(term, Function):
        return Function(term.name, [substitute(arg, subst) for arg in term.args])
    return term

def substitute_predicate(pred, subst):
    new_args = [substitute(arg, subst) for arg in pred.args]
    return Predicate(pred.name, new_args, pred.negated)

# ------------------------
# Resolution
# ------------------------

def resolve(ci, cj):
    resolvents = []
    for pi in ci.literals:
        for pj in cj.literals:
            if pi.name == pj.name and pi.negated != pj.negated:
                subst = unify(pi.args, pj.args, {})
                if subst is not None:
                    new_ci = [substitute_predicate(p, subst) for p in ci.literals if p != pi]
                    new_cj = [substitute_predicate(p, subst) for p in cj.literals if p != pj]
                    new_literals = list(set(new_ci + new_cj))
                    resolvent = Clause(new_literals)
                    resolvents.append(resolvent)
    return resolvents

def resolution(kb):
    clauses = list(kb)
    new = set()
    derived = set(clauses)

    while True:
        n = len(clauses)
        pairs = [(clauses[i], clauses[j]) for i in range(n) for j in range(i + 1, n)]
        for (ci, cj) in pairs:
            resolvents = resolve(ci, cj)
            for res in resolvents:
                if not res.literals:
                    return "no"
                if res not in derived:
                    new.add(res)
                    derived.add(res)
        if not new:
            return "yes"
        clauses.extend(new)
        new.clear()

# ------------------------
# Main Driver
# ------------------------

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 lab2.py KB.cnf")
        sys.exit(1)

    kb = parse_input(sys.argv[1])
    print(resolution(kb))

