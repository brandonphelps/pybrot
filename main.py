import math
import numpy
from color_test import colorer
from tqdm import tqdm
import time
import functools
from mandelbrot import func_z, find_iter

MAX_ITER = 100

from objects import ComplexNumber


def gen_grid(count, upper_left, lower_right):
    #for i in numpy.linspace(lower_left[0], upper_right[0], count):
    #    for j in numpy.linspace(lower_left[1], upper_right[1], count):
    for i in numpy.linspace(upper_left[0], lower_right[0], count):
        for j in numpy.linspace(upper_left[1], lower_right[1], count):
            yield (j, i)

def celery_construct_grid_coords(count, upper_left, lower_right):
    grid = []
    for j in tqdm(gen_grid(count, upper_left, lower_right), 'queing up jobs', total=count*count):
        grid.append(find_iter.delay(j[0], j[1], MAX_ITER))
    return grid

def celery_main(count):
    grid = celery_construct_grid_coords(count, (-2, 2), (2, -2))

    tasks_pending = True
    while tasks_pending:
        tasks_pending = False
        count_of_pending = 0
        for i in grid:
            if i.status == 'PENDING':
                tasks_pending = True
                count_of_pending += 1
        print("Waiting for tasks to finish: {}".format(count_of_pending))
        time.sleep(1)

    d2_array = []

    k = 0
    for i in tqdm(range(count), 'compiling results'):
        tmp = []
        for j in range(count):
            tmp.append(grid[k].result)
            k += 1
        d2_array.append(tmp)
    return d2_array

if __name__ == "__main__":
    new_grid = celery_main(100)
    colorer(new_grid)
