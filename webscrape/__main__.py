import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "cmd",
    default="client",
    choices=("client", "server"),
    help="What part of the code to run?",
)
parser.add_argument("--port", default=8000, type=int, help="Port to host web server at")
parser.add_argument(
    "--master-base",
    default="https://scrape.pyjaipur.org",
    type=str,
    help="Master server base url.",
)

args = parser.parse_args()
if args.cmd == "server":
    from webscrape import db, server
    import bottle_tools as bt

    tables = {
        "Question": db.Question,
        "Language": db.Language,
        "Submission": db.Submission,
        "Worker": db.Worker,
        "Job": db.Job,
        "Assignment": db.Assignment,
        "Pipeline": db.Pipeline,
    }
    bt.common_kwargs.update(tables)
    bt.common_kwargs["db"] = db.db
    db.db.create_tables(list(tables.values()))
    server.app.run(port=args.port, debug=True)
else:
    from webscrape import client

    worker = client.register_worker(args.master_base)
    worker.run()
