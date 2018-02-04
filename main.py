import math
import numpy
from color_test import colorer
from progress.bar import Bar
import functools

MAX_ITER = 100

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

@functools.lru_cache(maxsize=2000000)
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

def find_iter(complex_number):
    t = 1
    while not escape_mandelbrot(func_z(t, complex_number)):
        if t >= MAX_ITER:
            return t
        t += 1
    return t

def gen_grid(count):
    upper_left_x = -1.657
    upper_left_y = -.05
    lower_right_x = -1.55
    lower_right_y = .05
    for i in numpy.linspace(upper_left_x, lower_right_x, count):
        for j in numpy.linspace(upper_left_y, lower_right_y, count):
            yield (i, j)

def untested(count):
    return [-2 + (4/(count-1)) * x for x in range(0, count)]

if __name__ == "__main__":
    count = 10000
    grid = []

    bar = Bar('Processing', max=count * count)
    for j in gen_grid(count):
        grid.append(find_iter(ComplexNumber(*j)))
        bar.next()
    bar.finish()

    print(func_z.cache_info())
    
    new_grid = [[0 for i in range(count)] for j in range(count)]

    
    for index_col, col in enumerate(new_grid):
        for index_row, row in enumerate(col):
            new_grid[index_col][index_row] = grid[index_col * count + index_row]
    colorer(new_grid)

    # print("{} has an escape iter of: {}".format(t, find_iter(t)))
