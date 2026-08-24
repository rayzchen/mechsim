class Expression:
    context = []

    def __init__(self):
        pass

    def __str__(self):
        pass

    def contains(self, name):
        return False

    def copy(self):
        pass

    def substitute(self, values):
        pass

    def deriv(self, respect):
        pass

    def differentiate(self, respect):
        return self.deriv(respect).substitute({})

class Literal(Expression):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def contains(self, name):
        return False

    def copy(self):
        return Literal(self.value)

    def substitute(self, values):
        return self.copy()

    def deriv(self, respect):
        return Literal(0)

class Variable(Expression):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def contains(self, name):
        if name == self.name:
            return True
        elif name == "t" and self.name.replace("dot", "") in Expression.context:
            return True
        return False

    def copy(self):
        return Variable(self.name)

    def substitute(self, values):
        if self.name in values:
            return Literal(values[self.name])
        return self.copy()

    def deriv(self, respect):
        if self.name == respect:
            return Literal(1)
        elif respect == "t":
            return Variable(self.name + "dot")

class Power(Expression):
    def __init__(self, base, exponent):
        self.base = base
        self.exponent = exponent

    def __str__(self):
        return str(self.base) + "^" + str(self.exponent)

    def contains(self, name):
        return self.base.contains(name) or self.exponent.contains(name)

    def copy(self):
        return Power(self.base.copy(), self.exponent.copy())

    def substitute(self, values):
        new_base = self.base.substitute(values)
        new_exponent = self.exponent.substitute(values)
        if isinstance(new_base, Literal) and isinstance(new_base, Literal):
            return Literal(new_base.value ** new_exponent.value)
        return Power(new_base, new_exponent)

    def deriv(self, respect):
        if self.base.contains(respect):
            assert isinstance(self.exponent, Literal)
            if self.exponent.value == 2:
                return Term(2, [self.base, self.base.deriv(respect)])
            return Term(self.exponent.value, [Power(self.base, Literal(self.exponent.value - 1)), self.base.deriv(respect)])
        return Literal(0)

class Term(Expression):
    def __init__(self, coeff, terms):
        assert len(terms)
        self.coeff = coeff
        self.terms = terms

    def __str__(self):
        if self.coeff == -1:
            prefix = "-"
        elif self.coeff == 1:
            prefix = ""
        else:
            prefix = str(self.coeff)
        return prefix + "".join(map(str, self.terms))

    def contains(self, name):
        return any(term.contains(name) for term in self.terms)

    def copy(self):
        return Term(self.coeff, [term.copy() for term in self.terms])

    def substitute(self, values):
        new_terms = [term.substitute(values) for term in self.terms]
        new_coeff = self.coeff
        for term in new_terms:
            if isinstance(term, Literal):
                new_coeff *= term.value
            elif isinstance(term, Term):
                new_coeff *= term.coeff
                new_terms.extend(term.terms)
        new_terms = [term for term in new_terms if not isinstance(term, (Literal, Term))]
        if new_coeff == 0 or len(new_terms) == 0:
            return Literal(new_coeff)
        return Term(new_coeff, new_terms)

    def deriv(self, respect):
        functions = []
        constants = []
        for term in self.terms:
            if term.contains(respect):
                functions.append(term)
            else:
                constants.append(term)
        if not functions:
            return Literal(0)
        elif len(functions) == 1:
            deriv = functions[0].deriv(respect)
        elif len(functions) == 2:
            deriv = Sum([
                Term(1, [functions[0], functions[1].deriv(respect)]),
                Term(1, [functions[1], functions[0].deriv(respect)])
            ])
        elif len(functions) > 2:
            deriv = Term(1, [functions[0], Term(1, functions[1:])]).deriv(respect)
        return Term(self.coeff, constants + [deriv])

class Sum(Expression):
    def __init__(self, terms):
        assert len(terms)
        self.terms = terms

    def __str__(self):
        return " + ".join(map(str, self.terms)).replace("+ -", "- ")

    def contains(self, name):
        return any(term.contains(name) for term in self.terms)

    def copy(self):
        return Term([term.copy() for term in self.terms])

    def substitute(self, values):
        new_terms = [term.substitute(values) for term in self.terms]
        new_literal = Literal(0)
        for term in new_terms:
            if isinstance(term, Literal):
                new_literal.value += term.value
        new_terms = [term for term in new_terms if not isinstance(term, Literal)]
        if len(new_terms) == 0:
            return new_literal
        if new_literal.value == 0:
            if len(new_terms) == 1:
                return new_terms[0]
            else:
                return Sum(new_terms)
        return Sum(new_terms + [new_literal])

    def deriv(self, respect):
        new_terms = [term.deriv(respect) for term in self.terms]
        new_terms = [term for term in new_terms if not (isinstance(term, Literal) and term.value == 0)]
        if not new_terms:
            return Literal(0)
        elif len(new_terms) == 1:
            return new_terms[0]
        else:
            return Sum(new_terms)

def euler_lagrange(lagrangian):
    eqs = []
    for variable in Expression.context:
        term1 = lagrangian.differentiate(variable + "dot").differentiate("t")
        term2 = lagrangian.differentiate(variable)
        eqs.append(Sum([term1, Term(-1, [term2])]).substitute({}))
    return eqs

Expression.context = ["x"]
lagrangian = Sum([Term(0.5, [Variable("m"), Power(Variable("xdot"), Literal(2))]), Term(-1, [Variable("m"), Variable("g"), Variable("x")])])
for equation in euler_lagrange(lagrangian):
    print(equation, "= 0")
