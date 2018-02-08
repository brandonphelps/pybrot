import math
from json import JSONEncoder, JSONDecoder

class ComplexEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ComplexNumber):
            return [obj._real, obj._complex]
        return json.JSONEncoder.default(self, obj)

class ComplexDecoder(JSONDecoder):
    def default(self, obj):
        if isinstance(obj, list):

            return ComplexNumber(obj[0], obj[1])
        print("blahs")
        return json.JSONDecoder.default(self, obj)

class ComplexNumber:
    def __init__(self, real, complex):
        self._real = real
        self._complex = complex

    def __add__(self, other):
        return ComplexNumber(self._real + other._real,
                             self._complex + other._complex)

    def default(self, o):
        return {'real' : o._real, 'complex' : o._complex}

    def __mul__(self, other):
        temp = ComplexNumber(0, 0)
        temp._real = (self._real * other._real) - (self._complex * other._complex)
        temp._complex = (self._complex * other._real) + (self._real * other._complex)
        return temp

    def __abs__(self):
        return math.sqrt((self._real * self._real) + (self._complex * self._complex))

    def __str__(self):
        return "{} + {}i".format(self._real, self._complex)


if __name__ == "__main__":
    import json

    t = [ComplexNumber(2, 3)]

    s = json.dumps(t[0], cls=ComplexEncoder)
    print(s)
    c = json.loads(s, cls=ComplexDecoder)
    print(c)
