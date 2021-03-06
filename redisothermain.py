
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
        for i in tqdm(job['jobs']):
            results.append(find_iter(i['real'], i['imag'], int(i['max_iter'])))

        resultsz = serializer({'result' : results,
                               'job_id' : job['job_id']})

        self.redis_con.rpush(RESULT_Q_NAME, resultsz)
class Client:
    def __init__(self, redis_con):
        self.redis_con = redis_con
        self.finished_jobs = []

        self.jobs_added = 0
        self.jobs_pulled = 0
        self.max_fail_count = 10

    def post_job(self, job_posting, serializer=json.dumps, job_id=None):
        self.jobs_added += 1
        if job_id is None:
            job_id = str(uuid.uuid4().hex)
        job = {'job_id' : job_id}
        job.update({'jobs' : job_posting})
        if serializer is None:
            self.redis_con.rpush(JOB_Q_NAME, job)
        else:
            self.redis_con.rpush(JOB_Q_NAME, serializer(job))
        return job_id

    def get_result(self, timeout=0, deserializer=json.loads):
        job = self.redis_con.blpop(RESULT_Q_NAME, timeout=timeout)
        if job:
            job = deserializer(job[1].decode('utf-8'))
        return job

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
    if args.worker:
        w = Worker(r)
        w.start()
    if args.cli:
        c = Client(r)
        return_ids = []
        count = 10000
        job_size = 500
        all_jobs = {}
        gener = gen_grid(count, (-1.8125, .0625), (-1.625, -.0625))
        pixel_coord = (0, 0)
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
                    jobs.append({'real' : tmp[0], 'imag' : tmp[1], 'max_iter' : MAX_ITER})
                if jobs:
                    job_id = c.post_job(jobs)
                    return_ids.append(job_id)
                    all_jobs[job_id] = jobs
        result_grid = []
        tmp = []
        width = 0
        max_width = count
        finished_pool = []
        sorted_ids = list(return_ids)

        print("Gathering results")

        job_resend_counter = 0
        max_job_resend_count = 3

        with tqdm(total=len(return_ids)) as pbar:
            while return_ids:
                next_job = c.get_result(timeout=10)
                current_results = None
                if next_job:
                    for i in return_ids:
                        if i == next_job['job_id']:
                            return_ids.remove(i)
                            del all_jobs[i]
                            current_results = next_job
                            pbar.update(1)
                            break
                else:
                    job_resend_counter += 1
                    if job_resend_counter > max_job_resend_count:
                        for key, value in tqdm(all_jobs.items(), "Re submitting jobs"):
                            c.post_job(value, job_id=key)
                        job_resend_counter = 0
                    continue
                
                if current_results:
                    #todo: change this to a dict, where the keys are the job ids 
                    finished_pool.append(current_results)
        
        print("Sorting through results")
        
        height = 0
        with tqdm(total=len(sorted_ids)) as pbar:
            tmp = []
            for i in sorted_ids:
                for j in finished_pool:
                    if i == j['job_id']:
                        pbar.update(1)
                        for k in j['result']:
                            tmp.append(k)
                            height += 1
                            if height == count: # count also the width and height of the image
                                result_grid.append(tmp)
                                height = 0
                                tmp = []

        max_iter = max([max(row) for row in result_grid])
        min_iter = min([min(row) for row in result_grid])

        number_colors = {}

        unique_values = []
        for i in result_grid:
            for j in i:
                if j not in unique_values:
                    unique_values.append(j)

        unique_colors = 1
        for i in sorted(unique_values):
            if i not in number_colors.keys():
                number_colors[i] = unique_colors
                unique_colors += 1

        new_grid = []
        for i in result_grid:
            tmp = []
            for j in i:
                tmp.append(number_colors[j])
            new_grid.append(tmp)

        colorer(new_grid)
        
