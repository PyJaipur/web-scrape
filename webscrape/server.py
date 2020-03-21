import bottle
from functools import wraps
from bottle_tools import fill_args


app = bottle.Bottle()


def verify_worker(fn):
    @wraps(fn)
    @fill_args
    def fn_wrapper(worker_id: str, secret: str, Worker):
        w = Worker.get_or_none(Worker.id == worker_id, Worker.secret == secret)
        if w is None:
            bottle.abort(403, "This worker is not recognized")
        bottle.request.worker = worker
        return fn()

    return fn_wrapper


@app.get("/")
def stats():
    return "hi"


@app.post("/worker")
def create_new_worker_entry(secret: str, Worker):
    w = Worker.create(secret=secret)
    return {"worker_id": w.id}


@app.get("/batch")
@verify_worker
@fill_args
def get_a_job_batch_for_a_worker(worker_id: str, db, Assignment):
    # - Find jobs which have not been assigned
    sql = """
        select job.id, job.url, job.headers from job
        left join assignment a on a.job_id = job.id
        group by job.id
        having sum(a.completed) == 0
        order by count(a.id) asc
        limit 10
    """
    job_list = [
        {"job_id": job.id, "url": job.url, "headers": job.headers}
        for job in db.execute_sql(sql)
    ]
    # - create assignments for this worker
    assignment_list = Assignment.insert_many(
        [{"job_id": job["job_id"], "worker_id": worker_id} for job in job_list]
    ).execute()
    return {"jobs": job_list, "assignments": assignment_list.dicts()}


@app.post("/batch")
@verify_worker
@fill_args
def post_a_completed_batch(worker_id: int, jobs: list):
    pass
