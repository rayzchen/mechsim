class Expression:
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

class Variable(Expression):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def contains(self, name):
        return name == self.name

    def copy(self):
        return Variable(self.name)

    def substitute(self, values):
        if self.name in values:
            return Literal(values[self.name])
        return self.copy()

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
        new_terms = [term for term in new_terms if not isinstance(term, Literal)]
        if new_coeff == 0 or len(new_terms) == 0:
            return Literal(new_coeff)
        return Term(new_coeff, new_terms)

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
            return Sum(new_terms)
        return Sum(new_terms + [new_literal])
