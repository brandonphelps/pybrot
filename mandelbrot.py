
from celery import Celery
import getpass
import time
import math

t = '192.168.1.200'

app = Celery('mandel', broker='redis://192.168.1.200:6379/0',
             backend='redis://192.168.1.200:6379/0')


from objects import ComplexNumber

def base_value(obj):
    if type(obj) == int:
        return 0
    elif type(obj) == ComplexNumber:
        return ComplexNumber(0, 0)

#Todo: experiemntal can fail if not enough workers
@app.task
def func_z_celery(n, c):
    if n == 0:
        return base_value(c)
    else:
        k1 = func_z_celery.delay(n-1, c)
        while k1.status != 'SUCCESS':
            print("waiting for result on {} {}".format(n-1, c))
            time.sleep(1)
            if k1.status == 'FAILED':
                return 0
        return k1 * k1 + c

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

@app.task
def find_iter(real, imag, MAX_ITER):
    print("working on {} {}".format(real, imag))
    for i in range(1, MAX_ITER):
        print("Current iter: {}".format(i))
        if escape_mandelbrot(func_z(i, ComplexNumber(real, imag))):
            return i
    return MAX_ITER

