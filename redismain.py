from queue import Queue, Empty
import redis
import time
import uuid
import json
from threading import Thread
import argparse

class Worker:
    def __init__(self, redis_con):
        self._id = str(uuid.uuid4().hex)
        self.redis_con = redis_con
        self.pubsub = self.redis_con.pubsub()
        self.pubsub.subscribe(self._id)
        self.proc_thread = Thread(target=self.process_work)
        self.running = True
        self.request_work_timer_max = 20
        self.request_work_timer = 0

    def start(self):
        self.proc_thread.start()
        self.request_work()

    def stop(self):
        print("Worker: Stopping")
        self.running = False

    def process_work(self):
        while self.running:
            time.sleep(1)
            self.request_work_timer -= 1
            if self.request_work_timer <= 0:
                self.request_work()

            p = self.pubsub.get_message()
            if p:
                try:
                    print(p)
                    json_data = json.loads(p['data'].decode('utf-8'))
                except Exception as e:
                    continue
                self.do_work(json_data['user-job'])

    def do_work(self, job_info):
        print("WORKER: Doing the job {}".format(job_info))
        time.sleep(int(job_info))
        self.redis_con.publish('results', json.dumps({'id' : self._id,
                                                      'job_id' : 0,
                                                      'result' : job_info}))

    def request_work(self):
        print("Worker: Requsing more work")
        self.request_work_timer = self.request_work_timer_max
        self.redis_con.publish('needs-job', json.dumps({'needs-work' : self._id}))

class Manager:
    def __init__(self, redis_con):
        self.redis_con = redis_con
        self.pubsub = self.redis_con.pubsub()
        self.pubsub.subscribe('needs-job', 'user-job', 'results')
        self.quein = Thread(target = self.queu_work)
        self.process_subs_thread = Thread(target = self.process_sub)
        self.process_subs_running = True
        self.queu_jobs = True
        self.open_workers = Queue()
        self.jobs = Queue()

    def start(self):
        self.quein.start()
        self.process_subs_thread.start()

    def stop(self):
        print("Manager: Stopping")
        self.queu_jobs = False
        self.process_subs_running = False

    def process_sub(self):
        while self.process_subs_running:
            time.sleep(1)
            p = self.pubsub.get_message()
            try:
                json_data = json.loads(p['data'])
            except:
                continue
            if 'needs-work' in json_data.keys():
                self.update_workers(json_data)
            elif 'user-job' in json_data.keys():
                self.add_job(json_data)
            elif 'result' in json_data.keys():
                self.print_result(json_data)


    def update_workers(self, json_data):
        if 'needs-work' in json_data.keys():
            self.open_workers.put({'id' : json_data['needs-work']})

    def print_result(self, json_data):
        if 'result' in json_data.keys():
            print("Manager: Got result of job: {}".format(json_data['job_id']))
            print("Manager: Result {}".format(json_data['result']))

    def add_job(self, job_info):
        print("Manager: adding job {}".format(job_info))
        self.jobs.put(job_info)

    def queu_work(self):
        print("Waiting for workers")
        while self.queu_jobs:
            time.sleep(1)
            try:
                job = self.jobs.get(timeout=3)
            except Empty:
                continue
            try:
                k = self.open_workers.get(timeout=3)
            except Empty:
                self.jobs.put(job)
                continue

            print("{} found a worker for job {}".format(k, job))
            self.redis_con.publish(k['id'], json.dumps(job))

def post_job(redis_con, job_info):
    print("posting job: {}".format(job_info))
    redis_con.publish('user-job', job_info)





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
        time.sleep(500)
        w.stop()
    if args.manager:
        m = Manager(r)
        m.start()
        time.sleep(500)
        m.stop()
    if args.cli:
        post_job(r, json.dumps({'user-job': '1'}))
        post_job(r, json.dumps({'user-job': '1'}))
        post_job(r, json.dumps({'user-job': '2'}))
        post_job(r, json.dumps({'user-job': '3'}))
        post_job(r, json.dumps({'user-job': '5'}))
        post_job(r, json.dumps({'user-job': '4'}))



