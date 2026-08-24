import math
import itertools
import numpy as np

class Expression:
    context = []

    def __str__(self):
        pass

    def contains(self, name):
        return False

    def copy(self):
        pass

    def substitute(self, values):
        pass

    def evaluate(self, values):
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

    def evaluate(self, values):
        return self.value

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

    def evaluate(self, values):
        return values[self.name]

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
        assert isinstance(self.exponent, Literal)
        if isinstance(self.base, Sum):
            return Term(1, [self.base.copy()] * self.exponent.value).substitute(values)
        elif isinstance(self.base, Term):
            new_coeff = self.base.coeff ** self.exponent.value
            new_terms = [Power(term, self.exponent.copy()) for term in self.base.terms]
            return Term(new_coeff, new_terms).substitute(values)

        new_base = self.base.substitute(values)
        if isinstance(new_base, Literal):
            return Literal(new_base.value ** self.exponent.value)
        if self.exponent.value == 0:
            return Literal(1)
        return Power(new_base, self.exponent)

    def evaluate(self, values):
        return self.base.evaluate(values) ** self.exponent.evaluate(values)

    def deriv(self, respect):
        if self.base.contains(respect):
            assert isinstance(self.exponent, Literal)
            if self.exponent.value == 2:
                return Term(2, [self.base.copy(), self.base.deriv(respect)])
            return Term(self.exponent.value, [Power(self.base.copy(), Literal(self.exponent.value - 1)), self.base.deriv(respect)])
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
        sums = []
        variables = []
        for term in new_terms:
            if isinstance(term, Literal):
                new_coeff *= term.value
            elif isinstance(term, Term):
                new_coeff *= term.coeff
                new_terms.extend(term.terms)
            elif isinstance(term, Variable):
                variables.append(term)
            elif isinstance(term, Power):
                if isinstance(term.base, Variable):
                    variables.append(term)
            if isinstance(term, Sum):
                sums.append(term)

        new_terms = [term for term in new_terms if not isinstance(term, (Literal, Term))]
        if new_coeff == 0 or len(new_terms) == 0:
            return Literal(new_coeff)
        if new_coeff == 1 and len(new_terms) == 1:
            return new_terms[0]

        if sums:
            factors = [term for term in new_terms if not isinstance(term, Sum)]
            if factors:
                factors_term = Term(1, factors).substitute(values)
            else:
                factors_term = Literal(1)
            axes = [term.terms for term in sums]
            new_terms = []
            for product in itertools.product(*axes):
                new_terms.append(Term(new_coeff, [factors_term.copy()] + list(product)))
            return Sum(new_terms).substitute(values)

        if variables:
            new_terms = [term for term in new_terms if term not in variables]
            powers = {}
            for term in variables:
                if isinstance(term, Variable):
                    if term.name not in powers:
                        powers[term.name] = 1
                    else:
                        powers[term.name] += 1
                elif isinstance(term, Power):
                    assert isinstance(term.exponent, Literal)
                    if term.base.name not in powers:
                        powers[term.base.name] = term.exponent.value
                    else:
                        powers[term.base.name] += term.exponent.value
            prefix = []
            for name in powers:
                if powers[name] == 1:
                    prefix.append(Variable(name))
                else:
                    prefix.append(Power(Variable(name), Literal(powers[name])))
            new_terms = prefix + new_terms
        return Term(new_coeff, new_terms)

    def evaluate(self, values):
        result = self.coeff
        for term in self.terms:
            result *= term.evaluate(values)
        return result

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
        return "(" + " + ".join(map(str, self.terms)).replace("+ -", "- ") + ")"

    def contains(self, name):
        return any(term.contains(name) for term in self.terms)

    def copy(self):
        return Sum([term.copy() for term in self.terms])

    def substitute(self, values):
        new_terms = [term.substitute(values) for term in self.terms]
        new_literal = Literal(0)
        for term in new_terms:
            if isinstance(term, Literal):
                new_literal.value += term.value
            if isinstance(term, Sum):
                new_terms.extend(term.terms)
        new_terms = [term for term in new_terms if not isinstance(term, (Literal, Sum))]
        if len(new_terms) == 0:
            return new_literal
        if new_literal.value == 0:
            if len(new_terms) == 1:
                return new_terms[0]
            else:
                return Sum(new_terms)
        new_terms.append(new_literal)
        return Sum(new_terms)

    def evaluate(self, values):
        result = 0
        for term in self.terms:
            result += term.evaluate(values)
        return result

    def deriv(self, respect):
        new_terms = [term.deriv(respect) for term in self.terms]
        new_terms = [term for term in new_terms if not (isinstance(term, Literal) and term.value == 0)]
        if not new_terms:
            return Literal(0)
        elif len(new_terms) == 1:
            return new_terms[0]
        else:
            return Sum(new_terms)

class Function(Expression):
    def __init__(self, arg, name, func, deriv_class):
        self.arg = arg
        self.name = name
        self.func = func
        self.deriv_class = deriv_class

    def __str__(self):
        return self.name + "(" + str(self.arg) + ")"

    def contains(self, name):
        return self.arg.contains(name)

    def copy(self):
        return self.__class__(self.arg)

    def substitute(self, values):
        new_arg = self.arg.substitute(values)
        if isinstance(new_arg, Literal):
            return Literal(self.func(new_arg.value))
        return self.__class__(new_arg)

    def evaluate(self, values):
        return self.func(self.arg.evaluate(values))

    def deriv(self, respect):
        if self.arg.contains(respect):
            deriv = self.arg.deriv(respect)
            if isinstance(deriv, Literal) and deriv.value == 1:
                return self.deriv_class(self.arg.copy())
            return Term(1, [self.deriv_class(self.arg.copy()), deriv])
        return Literal(0)

def negative_wrapper(cls):
    def constructor(arg):
        return Term(-1, [cls(arg)])
    return constructor

class Sin(Function):
    def __init__(self, arg):
        super(Sin, self).__init__(arg, "sin", math.sin, Cos)

class Cos(Function):
    def __init__(self, arg):
        super(Cos, self).__init__(arg, "cos", math.cos, negative_wrapper(Sin))

def split_variable(term):
    if not isinstance(term, Term):
        return None, term
    for subterm in term.terms:
        if isinstance(subterm, Variable) and subterm.name.endswith("dotdot"):
            newterms = term.terms.copy()
            newterms.remove(subterm)
            if not newterms:
                return subterm.name, Literal(term.coeff)
            return subterm.name, Term(term.coeff, newterms)
    return None, term

def euler_lagrange(lagrangian):
    eqs = []
    for variable in Expression.context:
        term1 = lagrangian.differentiate(variable + "dot").differentiate("t")
        term2 = lagrangian.differentiate(variable)
        eq = Sum([term1, Term(-1, [term2])]).substitute({})

        coeffs = {variable + "dotdot": [] for variable in Expression.context}
        coeffs[None] = []
        for term in eq.terms:
            name, term = split_variable(term)
            coeffs[name].append(term)
        for name in coeffs:
            coeffs[name] = Sum(coeffs[name]).substitute({})
        eqs.append(coeffs)
    return eqs

def solve(equations, values):
    rank = len(Expression.context)
    matrix = np.zeros((rank, rank))
    constants = np.zeros((rank,))
    for i, coeffs in enumerate(equations):
        for j, variable in enumerate(Expression.context):
            matrix[i, j] = coeffs[variable + "dotdot"].evaluate(values)
        constants[i] = -coeffs[None].evaluate(values)

    return np.linalg.solve(matrix, constants).tolist()

Expression.context = ["theta1", "theta2"]
x2 = Sum([
    Term(1, [Variable("r1"), Sin(Variable("theta1"))]),
    Term(1, [Variable("r2"), Sin(Variable("theta2"))])
])
y2 = Sum([
    Term(1, [Variable("r1"), Cos(Variable("theta1"))]),
    Term(1, [Variable("r2"), Cos(Variable("theta2"))])
])
kinetic = Sum([
    Term(0.5, [Variable("m1"), Power(Variable("r1"), Literal(2)), Power(Variable("theta1dot"), Literal(2))]),
    Term(0.5, [Variable("m2"), Power(x2.differentiate("t"), Literal(2))]),
    Term(0.5, [Variable("m2"), Power(y2.differentiate("t"), Literal(2))])
])
potential = Sum([
    Term(-1, [Variable("m1"), Variable("g"), Variable("r1"), Cos(Variable("theta1"))]),
    Term(-1, [Variable("m2"), Variable("g"), y2]),
])
lagrangian = Sum([
    kinetic,
    Term(-1, [potential])
])

lagrangian = lagrangian.substitute({
    "m1": 1, "m2": 1,
    "g": 10,
    "r1": 0.5, "r2": 0.5,
})
equations = euler_lagrange(lagrangian)
for eq in equations:
    print(" + ".join(str(coeff) + (name if name else "") for name, coeff in eq.items()), "= 0")
