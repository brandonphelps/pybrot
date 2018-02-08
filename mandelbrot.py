
from celery import Celery
import getpass

# , backend='redis://192.168.1.200:6370')

t = '192.168.1.200'

app = Celery('mandel', broker='redis://127.0.0.1:6379/0',
             backend='redis://127.0.0.1:6379/0')

@app.task
def func_z(n, c):
    if n == 0:
        return base_value(c)
    else:
        return func_z(n-1, c) * func_z(n-1, c) + c
