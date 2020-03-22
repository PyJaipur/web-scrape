import bottle
import logging
from functools import wraps
from bottle_tools import fill_args
from webscrape.db import tables


log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)
app = bottle.Bottle()


def verify_worker(fn):
    @wraps(fn)
    @fill_args
    def fn_wrapper(worker_id: str, secret: str, Worker):
        worker = Worker.get_or_none(Worker.id == worker_id, Worker.secret == secret)
        if worker is None:
            bottle.abort(403, "This worker is not recognized")
        log.info(f"{worker_id:>5} {secret} : Verified")
        bottle.request.worker = worker
        return fn()

    return fn_wrapper


@app.get("/")
def stats():
    return "hi"


@app.post("/worker")
@fill_args
def create_new_worker_entry(secret: str, Worker):
    w = Worker.create(secret=secret)
    return {"worker_id": w.id}


@app.get("/batch")
@verify_worker
@fill_args
def get_a_job_batch_for_a_worker(worker_id: str, db, Assignment):
    # - Find jobs which have not been assigned
    sql = """
    select
      job.id,
      job.url,
      job.headers,
      p.py_before
    from
      job
    left join assignment a on
      a.job_id = job.id
    left join pipeline p on
      job.pipeline_id = p.id
    group by
      job.id
    having
      job.completed = 1
    order by
      count(a.id) asc
    limit 10
    """
    job_list = [
        {
            "job_id": job.id,
            "assignment_id": None,
            "url": job.url,
            "headers": job.headers,
            "before": job.py_before,
        }
        for job in db.execute_sql(sql)
    ]
    # - create assignments for this worker
    for job in job_list:
        assignment = Assignment.create(job_id=job["job_id"], worker_id=worker_id)
        job["assignment_id"] = assignment.id
    return {"jobs": job_list}


@app.post("/batch")
@verify_worker
@fill_args
def post_a_completed_batch(worker_id: int, assignments: list, Assignment, db):
    for assignment in assignments:
        job = Assignment.get_by_id(assignment["assignment_id"]).job
        # insert results into our database
        g = {}
        exec(job.pipeline.py_after, g)
        g["after"](db=db, pipeline_map=pipelines.MAP, **assignment["results"], **tables)
        # mark job as done
        job.completed = True
        job.save()
