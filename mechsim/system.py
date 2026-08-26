from mechsim.deriv import Var, Sin, Cos, Literal

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def differentiate(self, respect):
        return Vector(
            self.x.differentiate(respect),
            self.y.differentiate(respect)
        )

    def mag_squared(self):
        return self.x ** 2 + self.y ** 2

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        return NotImplemented
    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        return NotImplemented

    @staticmethod
    def polar(r, theta):
        x = r * Sin(theta)
        y = -r * Cos(theta)
        return Vector(x, y)

class Mass:
    def __init__(self, name):
        self.mass_var = Var(name)
        self.position = None

    def constrain_distance(self, name, length, centre=None):
        axis = Vector.polar(length, Var(name))
        if centre is None:
            self.position = axis
        else:
            self.position = centre + axis

    def constrain_horizontal(self, name, y=None):
        if y is None:
            y = Literal(0)
        self.position = Vector(Var(name), y)

    def constrain_vertical(self, name, x=None):
        if x is None:
            x = Literal(0)
        self.position = Vector(x, Var(name))

    def kinetic(self):
        velocity = self.position.differentiate("t")
        return 0.5 * self.mass_var * velocity.mag_squared()

    def potential(self):
        return self.mass_var * Var("g") * self.position.y

class Spring:
    def __init__(self, point1, point2, length, stiffness):
        self.point1 = point1
        self.point2 = point2
        self.length = length
        self.stiffness = stiffness

    def potential(self):
        distance2 = (self.point2 - self.point1).mag_squared()
        extension = distance2 ** 0.5 - self.length
        return 0.5 * self.stiffness * extension ** 2
