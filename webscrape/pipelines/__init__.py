from . import question_list
from . import question_page
from . import submission_list
from . import submission
from webscrape.db import Pipeline
import inspect

MAP = {}
for module in [question_list, question_page, submission_list, submission]:
    pipe = Pipeline.get_or_none(name=module.__name__)
    if pipe is None:
        pipe = Pipeline.create(
            name=module.__name__,
            py_before="def before(request):\n    pass",
            py_after="def after(*, db, pipeline_map, codes, Job, **_):\n    pass",
        )
    pipe.py_before = inspect.getsource(module.before)
    pipe.py_after = inspect.getsource(module.after)
    pipe.save()
    MAP[module.__name__] = module.pipeline = pipe
