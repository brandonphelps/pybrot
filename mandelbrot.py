
from celery import Celery
import getpass

t = '192.168.1.200'

app = Celery('mandel', broker='redis://192.168.1.200:6379/0',
             backend='redis://192.168.1.200:6379/0')


from objects import ComplexNumber


def base_value(obj):
    if type(obj) == int:
        return 0
    elif type(obj) == ComplexNumber:
        return ComplexNumber(0, 0)


@app.task
def func_z(n, c):
    if n == 0:
        return base_value(c)
    else:
        return func_z(n-1, c) * func_z(n-1, c) + c