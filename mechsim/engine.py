from mechsim.deriv import Variable, Literal, Term, Expression, Sum
import numpy as np

def split_variable(term):
    if isinstance(term, Variable) and term.name.endswith("dotdot"):
        return term.name, Literal(1)
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
        eq = (term1 - term2).substitute({})

        coeffs = {variable + "dotdot": [] for variable in Expression.context}
        coeffs[None] = []
        for term in eq.terms:
            name, term = split_variable(term)
            coeffs[name].append(term)

        row = []
        for name in coeffs:
            if coeffs[name]:
                row.append(Sum(coeffs[name]).substitute({}))
            else:
                row.append(Literal(0))
        eqs.append(row)
    return eqs

def display_equations(eqs):
    for row in eqs:
        line = ""
        for i in range(len(Expression.context)):
            line += str(row[i]) + Expression.context[i] + "dotdot + "
        line += str(row[-1])
        print(line, "= 0")

class Solver:
    def __init__(self, kinetic, potential):
        self.lagrangian = kinetic - potential
        self.equations = None
        self.context = Expression.context
        self.degrees = len(self.context)
        self.params = np.zeros((self.degrees,))
        self.param_derivs = np.zeros((self.degrees,))

    def load_constants(self, values):
        self.lagrangian = self.lagrangian.substitute(values)
        self.equations = euler_lagrange(self.lagrangian)

    def load_initial_values(self, params, param_derivs):
        self.params = np.array(params)
        self.param_derivs = np.array(param_derivs)

    def solve(self):
        values = {name: self.params[i] for i, name in enumerate(self.context)}
        values.extend({name + "dot": self.param_derivs[i] for i, name in enumerate(self.context)})
        matrix = np.zeros((self.degrees, self.degrees))
        constants = np.zeros((self.degrees,))
        for i in range(self.degrees):
            for j in range(self.degrees):
                matrix[i, j] = self.equations[i][j].evaluate(values)
            constants[i] = -self.equations[i][self.degrees].evaluate(values)
        return np.linalg.solve(matrix, constants)
