import math
import numpy
from color_test import colorer
from progress.bar import Bar
from tqdm import tqdm
import time
import functools
from mandelbrot import func_z

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

def translate_coords(c1,c2):
    return (c1[0], c2[1]), (c2[0], c1[1])

def main():
    grid = []
    count = 2000

    upper_left = (-1.750, 0.01)
    lower_right = (-1.55225, -0.01)
    
    for j in tqdm(gen_grid(count, upper_left, lower_right), total=(count*count)):
        grid.append(find_iter(ComplexNumber(*j)))

    print(func_z.cache_info())
    
    new_grid = []

    tmp = []
    for index, j in enumerate(grid):
        tmp.append(j)
        if index % count == count - 1:
            new_grid.append(tmp)
            tmp = []

    colorer(new_grid)

def oned_to_twod(width, height):

    lower_left = (0, 0)
    upper_right = (10, 10)
    
    for width_index, i in enumerate(numpy.linspace(lower_left[0], width, width)):
        for j in numpy.linspace(lower_left[0], height, height):
            print("({:5.2f}, {:5.2f}) ".format(i, j), end="")
            yield (i, j)
        print("")
        

if __name__ == "__main__":
    main()
    width = 10
    height = 5
    oned_r = [i for i in oned_to_twod(width, height)]

    print("printing one d")

    twod_r = []

    
    tmp = []

    for index, j in enumerate(oned_r):
        tmp.append(j)
        print("({:5.2f}, {:5.2f}) ".format(j[0], j[1]), end="")
        if index % height == height - 1:
            twod_r.append(tmp)
            tmp = []
            print("")

    print("printing two d")
    for row in twod_r:
        print(row)


    # main()
    # print("{} has an escape iter of: {}".format(t, find_iter(t)))
