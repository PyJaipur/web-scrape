from . import question_list
from . import question_page
from . import submission_list
from . import submission
from webscrape.db import Pipeline
import inspect

MAP = {}
for module in [question_list, question_page, submission_list, submission]:
    module.pipeline, created = Pipeline.get_or_create(name=module.__name__,)
    module.pipeline.py_before = inspect.getsource(module.before)
    module.pipeline.py_after = inspect.getsource(module.after)
    module.pipeline.save()
    MAP[module.__name__] = module.pipeline
