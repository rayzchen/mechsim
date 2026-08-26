from mechsim.deriv import Var, Sin, Cos, Literal

def conv(value):
    if isinstance(value, (float, int)):
        return Literal(value)
    return value

class Vector:
    def __init__(self, x, y):
        self.x = conv(x)
        self.y = conv(y)

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

    def rotate(self, angle):
        x = self.x * Cos(angle) + self.y * Sin(angle)
        y = self.x * -Sin(angle) + self.y * Cos(angle)
        return Vector(x, y)

    @staticmethod
    def polar(r, theta):
        x = conv(r) * Sin(conv(theta))
        y = -conv(r) * Cos(conv(theta))
        return Vector(x, y)

class Mass:
    def __init__(self, name):
        self.mass_var = Var(name)
        self.position = None

    def constrain_offset(self, name, offset, centre=None):
        axis = offset.rotate(Var(name))
        if centre is None:
            self.position = axis
        else:
            self.position = centre + axis

    def constrain_horizontal(self, name, y=0):
        self.position = Vector(Var(name), y)

    def constrain_vertical(self, name, x=0):
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
        self.length = conv(length)
        self.stiffness = conv(stiffness)

    def potential(self):
        distance2 = (self.point2 - self.point1).mag_squared()
        extension = distance2 ** 0.5 - self.length
        return 0.5 * self.stiffness * extension ** 2
