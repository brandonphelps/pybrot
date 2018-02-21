from queue import Queue, Empty
import redis
import time
import uuid
import json
from threading import Thread


class Worker:
    def __init__(self, redis_con):
        self._id = str(uuid.uuid4().hex)
        self.redis_con = redis_con
        self.pubsub = self.redis_con.pubsub()
        self.pubsub.subscribe(self._id)
        self.proc_thread = Thread(target=self.process_work)
        self.running = True

    def start(self):
        self.proc_thread.start()
        self.request_work()

    def stop(self):
        print("Worker: Stopping")
        self.running = False

    def process_work(self):
        while self.running:
            time.sleep(1)
            p = self.pubsub.get_message()
            if p:
                try:
                    print(p)
                    json_data = json.loads(p['data'])
                except Exception as e:
                    continue
                self.do_work(json_data['user-job'])

    def do_work(self, job_info):
        print("WORKER: Doing the job {}".format(job_info))
        time.sleep(int(job_info))
        self.request_work()

    def request_work(self):
        print("Worker: Requsing more work")
        self.redis_con.publish('needs-job', json.dumps({'needs-work' : self._id}))

class Manager:
    def __init__(self, redis_con):
        self.redis_con = redis_con
        self.pubsub = self.redis_con.pubsub()
        self.pubsub.subscribe('needs-job', 'user-job')
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

    def update_workers(self, json_data):
        if 'needs-work' in json_data.keys():
            self.open_workers.put({'id' : json_data['needs-work']})

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
    r = redis.StrictRedis(host='192.168.1.200', port=6379, db=0)
    m = Manager(r)

    w = Worker(r)

    m.start()
    w.start()
    post_job(r, json.dumps({'user-job': '10'}))
    post_job(r, json.dumps({'user-job': '10'}))
    post_job(r, json.dumps({'user-job': '20'}))
    post_job(r, json.dumps({'user-job': '30'}))
    post_job(r, json.dumps({'user-job': '50'}))
    post_job(r, json.dumps({'user-job': '40'}))
    time.sleep(500)
    m.stop()
    w.stop()
