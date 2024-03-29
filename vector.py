import math


class Vector(object):
    def __init__(self, x=0., y=0.):
        self.x = x
        self.y = y
        self.thresh = 0.000001

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        if scalar != 0:
            return Vector(self.x / float(scalar), self.y / float(scalar))
        return None

    def __eq__(self, other):
        if abs(self.x - other.x) < self.thresh:
            if abs(self.y - other.y) < self.thresh:
                return True
        return False

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def magnitude_squared(self):
        return self.x ** 2 + self.y ** 2

    def magnitude(self):
        return math.sqrt(self.magnitude_squared())

    def copy(self):
        return Vector(self.x, self.y)

    def as_tuple(self):
        return self.x, self.y

    def as_int(self):
        return int(self.x), int(self.y)


class NullVector(Vector):

    def __init__(self):
        super(NullVector, self).__init__(0, 0)
