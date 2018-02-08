import math
import numpy
from color_test import colorer
from progress.bar import Bar
from tqdm import tqdm
import time
import functools
from mandelbrot import func_z

MAX_ITER = 1000

from objects import ComplexNumber


def escape_mandelbrot(complex_number):
    tmp = abs(complex_number) 
    if tmp  < 2:
        return False
    else:
        return True


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


def celery_construct_grid_coords(count, upper_left, lower_right):
    grid = []
    for j in tqdm(gen_grid(count, upper_left, lower_right), total=(count*count)):
        grid.append(find_iter.delay(ComplexNumber(*j)))
    return grid

def celery_main():
    grid = construct_grid_coords(2000, (-2, 2), (2, -2))

    resultant_grid = [0 for i in range(len(grid))]

    still_working = True
    while still_working:
        still_working = False
        for index, i in enumerate(grid):
            try:
                if i.status == 'SUCCESS':
                   grid[index] = i.result
                elif i.status == 'FAILURE':
                    grid[index] = 1
                elif i.status == 'PENDING' or i.status == 'STARTED' or i.status == 'RETRY':
                    still_working = True
            except:
                pass
    return grid

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
    celery_main()
