import random
import arrow
import string
import peewee as pw

db = pw.PostgresqlDatabase("pyj", user="root")


def randstr(k=5):
    return "".join(random.sample(string.ascii_letters, k))


class Base(pw.Model):
    class Meta:
        database = db


# Crawl target dataset


class Question(Base):
    code = pw.CharField()
    statement = pw.TextField()


class Language(Base):
    name = pw.CharField()


class Submission(Base):
    question = pw.ForeignKeyField(Question)
    lang = pw.ForeignKeyField(Language)
    result = pw.CharField()
    code = pw.TextField()
    md5 = pw.CharField()


# Crawling infra


class Worker(Base):
    name = pw.CharField(default=randstr)


class Job(Base):
    url = pw.CharField()
    headers = pw.CharField()
    complete = pw.BooleanField(default=False)


class Assignment(Base):
    worker = pw.ForeignKeyField(Worker)
    job = pw.ForeignKeyField(Job)
    assigned_at = pw.DateTimeField(default=arrow.utcnow)
