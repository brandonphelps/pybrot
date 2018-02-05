import math
import numpy
from color_test import colorer
from progress.bar import Bar
from tqdm import tqdm
import time
import functools

MAX_ITER = 1000

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
    for i in range(1, MAX_ITER):
        if escape_mandelbrot(func_z(i, complex_number)):
            return i
    return MAX_ITER

def gen_grid(count, lower_left, upper_right):
    lower_left_x = -1.657
    lower_left_y = -.05
    upper_right_x = -1.55
    upper_right_y = .05
    #print(lower_left)
    #print(upper_right)
    for i in numpy.linspace(lower_left[0], upper_right[0], count):
        for j in numpy.linspace(lower_left[1], upper_right[1], count):
            yield (i, j)

def zoom_box(x, y, width, height):
    #lower_left_x = -1.657
    #lower_left_y = -.05
    #upper_right_x = -1.55
    #upper_right_y = .05

    lower_left_x = (x - (width / 2))
    upper_right_x = (x + (width / 2))
    lower_left_y = (y - (height / 2))
    upper_right_y = (y + (height / 2))
    
    return (lower_left_x, lower_left_y), (upper_right_x, upper_right_y)

def main():
    grid = []
    count = 1000
    #zoom = zoom_box(-1.65, 0, 2, 2)
    #print("Zoom box: {}".format(zoom))
    for j in tqdm(gen_grid(count, (-1.757, -0.5), (-0.5, .05)), total=(count*count)):
        grid.append(find_iter(ComplexNumber(*j)))

    print(func_z.cache_info())
    
    new_grid = [[0 for i in range(count)] for j in range(count)]

    
    for index_col, col in enumerate(new_grid):
        for index_row, row in enumerate(col):
            new_grid[index_col][index_row] = grid[index_col * count + index_row]
    colorer(new_grid)

def test_iter():
    for i in range(1000):
        yield i
    

if __name__ == "__main__":
    main()
    # print("{} has an escape iter of: {}".format(t, find_iter(t)))
