
class ComplexNumber:
    def __init__(self, real, complex):
        self._real = real
        self._complex = complex

    def __add__(self, other):
        return ComplexNumber(self._real + other._real,
                             self._complex + other._complex)

    def __mul__(self, other):
        temp = ComplexNumber(0, 0)
        temp._real = (self._real * other._real) - (self._complex * other._complex)
        temp._complex = (self._complex * other._real) + (self._real * other._complex)
        return temp

    def __abs__(self):
        return math.sqrt((self._real * self._real) + (self._complex * self._complex))

    def __str__(self):
        return "{} + {}i".format(self._real, self._complex)
