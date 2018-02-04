import math
import numpy

import functools

MAX_ITER = 30

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


def base_value(obj):
    if type(obj) == int:
        return 0
    elif type(obj) == ComplexNumber:
        return ComplexNumber(0, 0)

@functools.lru_cache(maxsize=20000)
def func_z(n, c):
    if n == 0:
        return base_value(c)
    else:
        return func_z(n-1, c) * func_z(n-1, c) + c

def escape_mandelbrot(complex_number):
    tmp = abs(complex_number) 
    if tmp  < 2:
        return False
    else:
        return True

@functools.lru_cache(maxsize=4098)
def find_iter(complex_number):
    t = 1
    while not escape_mandelbrot(func_z(t, complex_number)):
        if t >= MAX_ITER:
            return t
        t += 1
    return t

def gen_grid(count):
    val = 1
    for i in numpy.linspace(-1 * val, val, count):
        for j in numpy.linspace(-1 * val, val, count):
            yield (i, j)

def untested(count):
    return [-2 + (4/(count-1)) * x for x in range(0, count)]
            
if __name__ == "__main__":

    count = 111
    i = 0
    grid = []
    
    for j in gen_grid(count):
        grid.append(find_iter(ComplexNumber(*j)))
        i += 1

    for j in range(count):
        for i in range(count):
            print("{:2}".format(grid[i * count + j]), end="")
        print("")
    

    # print("{} has an escape iter of: {}".format(t, find_iter(t)))
