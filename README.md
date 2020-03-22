Web Scrape
==========

- One master server.
- Multiple "workers" which supply scraping network bandwidth + processing power.
- How to update worker code?
    - Server sends the before/after parts of the job processing pipeline to the workers.
    - This code is maintained in normal python code.
- Insert obtained data into database + create more jobs.
