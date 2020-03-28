def before(response):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(response.text, "lxml")
    table = soup.find("table", {"class": "dataTable"})
    codes = []
    for row in table.findAll("tr"):
        tds = list(row.findAll("td"))
        if len(tds) > 1:
            codes.append(tds[1].text)
    return {"codes": codes}


def after(*, db, pipeline_map, codes, Job, **_):
    pipe = pipeline_map["webscrape.pipelines.question_page"]
    jobs = [
        {
            "url": f"https://www.codechef.com/problems/{code}",
            "headers": "{}",
            "pipeline": pipe,
        }
        for code in codes
    ]
    Job.insert_many(jobs)
