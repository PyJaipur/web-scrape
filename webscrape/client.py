import requests
import logging
import time
import random
import string
from collections import namedtuple

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

Job = namedtuple("Job", "job_id assignment_id process result")
Worker = namedtuple("Worker", "secret worker_id run")


def make_secret(k=20):
    return "".join(random.sample(string.ascii_letters, k))


def register_worker(base, sleep_n=5):
    secret = make_secret()
    r = requests.post(f"{base}/worker", json={"secret": secret})
    worker_id = r.json()["worker_id"]
    auth = {"secret": secret, "worker_id": worker_id}
    log.info(f"{worker_id} registered with secret {secret}")
    # =====================
    def get_batch():
        r = requests.get(f"{base}/batch", params=auth)
        if r.status_code != 200:
            return []
        batch = r.json()
        jobs = []
        for job in batch["jobs"]:

            def process():
                r = requests.get(job["url"], headers=job["headers"])
                g = {}
                exec(batch["pipelines"][job["pipeline_id"]], g)
                results = g["before"](r)
                return Job(job["job_id"], job["assignment_id"], None, results)

            job = Job(job["job_id"], job["assignment_id"], run, None)
            jobs.append(job)
        return jobs

    def process_batch(batch):
        results = []
        for job in batch:
            finished_job = job.process()
            results.append(finished_job)
        return results

    def post_results(results):
        requests.post(
            f"{base}/batch",
            json={
                "results": [
                    {"assignment_id": job.assignment_id, "returned": job.results}
                    for job in results
                ],
                **auth,
            },
        )

    def run():
        while True:
            jobs = get_batch()
            log.info(f"Got {len(jobs)} jobs.")
            if not jobs:
                log.info(f"Sleeping for {sleep_n} seconds")
                time.sleep(sleep_n)
            else:
                results = process_batch(jobs)
                post_results(results)
                log.info(f"Done")

    return Worker(secret, worker_id, run)
