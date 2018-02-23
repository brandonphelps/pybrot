
import redis
import uuid
import time
import argparse
import json
from datetime import datetime
from mandelbrot import find_iter
import numpy
from tqdm import tqdm
from color_test import colorer
import pprint

JOB_Q_NAME = 'jobs'
RESULT_Q_NAME = 'results'

MAX_ITER = 10000

class Worker:
    def __init__(self, redis_con):
        self._id = str(uuid.uuid4().hex)
        self.redis_con = redis_con
        self.running = True

    def start(self):
        while self.running:
            s = datetime.now()
            self.do_work()
            e = datetime.now()
            print("total: {}".format(e - s))

    def do_work(self, serializer=json.dumps, deserializer=json.loads):
        print("Attempting to get another job")
        if deserializer:
            job = self.redis_con.blpop(JOB_Q_NAME)
            job = deserializer(job[1])
        else:
            #todo:
            pass
        results = []
        for i in job['jobs']:
            results.append(find_iter(i['real'], i['imag'], MAX_ITER))

        self.redis_con.rpush(RESULT_Q_NAME, serializer({'result' : results,
                                                        'job_id' : job['job_id']}))

class Client:
    def __init__(self, redis_con):
        self.redis_con = redis_con
        self.finished_jobs = []

    def post_job(self, job_posting, serializer=json.dumps):
        job_id = str(uuid.uuid4().hex)
        job = {'job_id' : job_id}
        job.update({'jobs' : job_posting})
        if serializer is None:
            self.redis_con.rpush(JOB_Q_NAME, job)
        else:
            self.redis_con.rpush(JOB_Q_NAME, serializer(job))
        return job_id

    def get_all_results(self, deserializer=json.loads):
        while True:
            job = self.redis_con.blpop(RESULT_Q_NAME, timeout=1)
            if job is None:
                break
            yield deserializer(job[1])

    def clear(self):
        self.redis_con.delete(JOB_Q_NAME)
        self.redis_con.delete(RESULT_Q_NAME)

def gen_grid(count, upper_left, lower_right):
    for i in numpy.linspace(upper_left[0], lower_right[0], count):
        for j in numpy.linspace(upper_left[1], lower_right[1], count):
            yield (i, j)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--worker', action='store_true')
    group.add_argument('--manager', action='store_true')
    group.add_argument('--cli', action='store_true')

    args = parser.parse_args()

    r = redis.StrictRedis(host='192.168.1.200', port=6379, db=0)
    if args.worker:
        w = Worker(r)
        w.start()
    if args.cli:
        c = Client(r)
        c.clear()

        return_ids = []
        count = 100
        job_size = 100
        gener = gen_grid(count, (-2, 2), (2, -2))
        keep_posing = True
        while keep_posing:
            jobs = []
            for i in range(job_size):
                try:
                    tmp = next(gener)
                except StopIteration:
                    keep_posing = False
                    break
                
                jobs.append({'real' : tmp[0], 'imag' : tmp[1]})
            if jobs:
                return_ids.append(c.post_job(jobs))

        

        current_id = return_ids.pop(0)
        all_results = list(c.get_all_results())
        result_grid = []
        tmp = []
        width = 0
        max_width = count
        while return_ids:
            print("Searching for id: {}".format(current_id))
            for i in all_results:
                if i['job_id'] == current_id:
                    for j in i['result']:
                        tmp.append(j)
                        width += 1
                        if width == max_width:
                            result_grid.append(tmp)
                            width = 0
                            tmp = []
            current_id = return_ids.pop(0)

        pprint.pprint(result_grid)
        colorer(result_grid)
        
