import requests
from webscrape import __version__
from webscrape.pipelines import question_list


def test_version():
    assert __version__ == "0.1.0"


def test_question_link_pipe_works():
    url = "https://www.codechef.com/problems/school"
    r = requests.get(url)
    question_list.before(r)
