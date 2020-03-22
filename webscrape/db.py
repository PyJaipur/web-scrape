import os
import random
import arrow
import string
import peewee as pw
from playhouse.sqlite_ext import SqliteExtDatabase

env = os.environ.get

# db = pw.PostgresqlDatabase("webscrape", user="pyjaipur", password="password!")
db = SqliteExtDatabase(
    "pyjaipur.sqlitedb",
    pragmas=(
        ("cache_size", -1024 * 64),  # 64MB page-cache.
        ("journal_mode", "wal"),  # Use WAL-mode (you should always use this!).
        ("foreign_keys", 1),
    ),
)


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
    question = pw.ForeignKeyField(Question)
    lang = pw.ForeignKeyField(Language)
    result = pw.CharField()
    code = pw.TextField()
    md5 = pw.CharField()


# Crawling infra


class Worker(Base):
    "A worker who is willing to extract some code"
    secret = pw.CharField()


class Pipeline(Base):
    "What to do before/after a network request is made"
    py_before = pw.TextField()
    py_after = pw.TextField()


class Job(Base):
    "A request job"
    url = pw.CharField()
    headers = pw.CharField()
    completed = pw.BooleanField(default=False)
    pipeline = pw.ForeignKeyField(Pipeline)


class Assignment(Base):
    "A job is issued to some worker"
    worker = pw.ForeignKeyField(Worker)
    job = pw.ForeignKeyField(Job)
    assigned_at = pw.DateTimeField(default=arrow.utcnow)
