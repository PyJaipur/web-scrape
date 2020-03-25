import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "cmd",
    default="client",
    choices=("client", "server", "qlist"),
    help="What part of the code to run?",
)
parser.add_argument(
    "--url",
    default=None,
    type=str,
    help="Used with the qlist command. What url to add as a question list job.",
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
    from webscrape.db import db, tables

    with db:
        db.create_tables(list(tables.values()))
        from webscrape import server, pipelines
        import bottle_tools as bt

        bt.common_kwargs.update(tables)
        bt.common_kwargs["db"] = db
        # TODO(thesage21): move to a per request connection pool

    @server.app.hook("before_request")
    def _connect_db():
        db.connect()

    @server.app.hook("after_request")
    def _close_db():
        if not db.is_closed():
            db.close()

    server.app.run(port=args.port, debug=True)
elif args.cmd == "client":
    from webscrape import client

    worker = client.register_worker(args.master_base)
    worker.run()
elif args.cmd == "qlist":
    assert args.url is not None
    from webscrape.db import db, tables, Job

    with db:
        db.create_tables(list(tables.values()))

        from webscrape.pipelines import question_list

        Job.create(url=args.url, headers="{}", pipeline=question_list.pipeline)
