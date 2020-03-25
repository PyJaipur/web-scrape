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
def get_a_job_batch_for_a_worker(worker_id: str, db, Assignment, Pipeline):
    # - Find jobs which have not been assigned
    sql = """
    select
      job.id,
      job.url,
      job.headers,
      job.pipeline_id
    from
      job
    left join assignment a on
      a.job_id = job.id
    group by
      job.id
    having
      job.completed = false
    order by
      count(a.id) asc
    limit 10
    """
    job_list = [
        {
            "job_id": id,
            "assignment_id": None,
            "url": url,
            "headers": headers,
            "pipeline_id": pipe_id,
        }
        for id, url, headers, pipe_id in db.execute_sql(sql)
    ]
    # - create assignments for this worker
    for job in job_list:
        assignment = Assignment.create(job_id=job["job_id"], worker_id=worker_id)
        job["assignment_id"] = assignment.id
    pipes = {j["pipeline_id"] for j in job_list}
    return {
        "jobs": job_list,
        "pipelines": {
            p.name: p.py_before
            for p in Pipeline.select().where(Pipeline.name.in_(pipes))
        },
    }


@app.post("/batch")
@verify_worker
@fill_args
def post_a_completed_batch(worker_id: int, results: list, Assignment, db):
    for assignment in assignments:
        job = Assignment.get_by_id(assignment["assignment_id"]).job
        if job.completed:
            continue
        # insert results into our database
        g = {}
        exec(job.pipeline.py_after, g)
        g["after"](
            db=db, pipeline_map=pipelines.MAP, **assignment["returned"], **tables
        )
        # mark job as done
        job.completed = True
        job.save()
