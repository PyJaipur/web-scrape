import argparse
from webscrape import db, server
import bottle_tools as bt

tables = {
    "Base": Base,
    "Question": Question,
    "Language": Language,
    "Submission": Submission,
    "Worker": Worker,
    "Job": Job,
    "Assignment": Assignment,
    "db": db.db,
}
bt.common_kwargs.update(tables)
db.db.create_tables(list(tables.values()))


parser = argparse.ArgumentParser()
parser.add_argument("--port", default=8000, type=int, help="Port to host web server at")

args = parser.parse_args()
