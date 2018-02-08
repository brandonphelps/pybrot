
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
    c = 0
    z = ComplexNumber(0, 0)
    while abs(z) <= 2.0:
        print("Current iter: {}".format(i))
        c += 1
        if c > MAX_ITER:
            break
        z = z * z + c 
    return c

