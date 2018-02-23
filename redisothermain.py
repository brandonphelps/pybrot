
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
        if deserializer:
            job = self.redis_con.blpop(JOB_Q_NAME)
            job = deserializer(job[1].decode('utf-8'))
        else:
            #todo:
            pass
        results = []
        print("Doing job: {}".format(job['job_id']))
        for i in job['jobs']:
            results.append(find_iter(i['real'], i['imag'], MAX_ITER))

        self.redis_con.rpush(RESULT_Q_NAME, serializer({'result' : results,
                                                        'job_id' : job['job_id']}))

class Client:
    def __init__(self, redis_con):
        self.redis_con = redis_con
        self.finished_jobs = []

        self.jobs_added = 0
        self.jobs_pulled = 0
        self.max_fail_count = 10

    def post_job(self, job_posting, serializer=json.dumps):
        self.jobs_added += 1
        job_id = str(uuid.uuid4().hex)
        job = {'job_id' : job_id}
        job.update({'jobs' : job_posting})
        if serializer is None:
            self.redis_con.rpush(JOB_Q_NAME, job)
        else:
            self.redis_con.rpush(JOB_Q_NAME, serializer(job))
        return job_id

    def get_result(self, deserializer=json.loads):
        job = self.redis_con.blpop(RESULT_Q_NAME)
        return deserializer(job[1].decode('utf-8'))

    def get_all_results(self, deserializer=json.loads):
        timeout = 1
        fail_count = 0
        while True:
            job = self.redis_con.blpop(RESULT_Q_NAME, timeout=timeout)
            if job is None:
                if self.jobs_pulled < self.jobs_added:
                    timeout = timeout * 2
                    fail_count += 1
                    if fail_count > self.max_fail_count:
                        break
                else:
                    break
            else:
                self.jobs_pulled += 1
                timeout = timeout // 2
                if timeout <= 0:
                    timeout = 1
            if job:
                yield deserializer(job[1].decode('utf-8'))

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
    r.flushall()

    if args.worker:
        w = Worker(r)
        w.start()
    if args.cli:
        c = Client(r)
        return_ids = []
        count = 100
        job_size = 10
        gener = gen_grid(count, (-2, 2), (2, -2))
        keep_posing = True
        with tqdm(total=count*count) as pbar:
            while keep_posing:
                jobs = []
                for i in range(job_size):
                    try:
                        tmp = next(gener)
                        pbar.update(1)
                    except StopIteration:
                        keep_posing = False
                        break
                
                    jobs.append({'real' : tmp[0], 'imag' : tmp[1]})
                if jobs:
                    return_ids.append(c.post_job(jobs))
        result_grid = []
        tmp = []
        width = 0
        max_width = count
        with tqdm(total=len(return_ids)) as pbar:
            while return_ids:
                next_job = c.get_result()
                new_ids = []
                for i in return_ids:
                    if i == next_job['job_id']:
                        current_results = next_job['result']
                        pbar.update(1)
                    else:
                        new_ids.append(i)
                return_ids = new_ids

                for j in current_results:
                    tmp.append(j)
                    width += 1
                    if width == max_width:
                        result_grid.append(tmp)
                        width = 0
                        tmp = []
        colorer(result_grid)
        
