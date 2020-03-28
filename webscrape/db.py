import os
import random
from datetime import datetime
import string
import peewee as pw
from playhouse.db_url import connect

env = os.environ.get
pwd = env("PGSQL_PASSWORD", "secret")
# db = connect(f"postgresext+pool://admin:{pwd}@localhost:54322/postgres")
db = pw.SqliteDatabase("temp.sqlite", pragmas={"journal_mode": "wal"})


def randstr(k=5):
    return "".join(random.sample(string.ascii_letters, k))


class Base(pw.Model):
    class Meta:
        database = db


# Crawl target dataset


class Question(Base):
    "A question on codechef"
    code = pw.CharField()
    statement = pw.TextField()


class Language(Base):
    "A language used on codechef. Python/cpp/c/java etc"
    name = pw.CharField()


class Submission(Base):
    "A submission by someone"
    question = pw.ForeignKeyField(Question, on_delete="CASCADE")
    lang = pw.ForeignKeyField(Language, on_delete="CASCADE")
    result = pw.CharField()
    code = pw.TextField()
    md5 = pw.CharField()


# Crawling infra


class Worker(Base):
    "A worker who is willing to extract some code"
    secret = pw.CharField()


class Pipeline(Base):
    "What to do before/after a network request is made"
    name = pw.CharField(primary_key=True)
    py_before = pw.TextField()
    py_after = pw.TextField()


class Job(Base):
    "A request job"
    url = pw.CharField()
    headers = pw.CharField()
    completed = pw.BooleanField(default=False)
    pipeline = pw.ForeignKeyField(Pipeline, on_delete="CASCADE")


class Assignment(Base):
    "A job is issued to some worker"
    worker = pw.ForeignKeyField(Worker, on_delete="CASCADE")
    job = pw.ForeignKeyField(Job, on_delete="CASCADE")
    assigned_at = pw.DateTimeField(default=datetime.utcnow)


tables = {
    "Question": Question,
    "Language": Language,
    "Submission": Submission,
    "Worker": Worker,
    "Job": Job,
    "Assignment": Assignment,
    "Pipeline": Pipeline,
}
