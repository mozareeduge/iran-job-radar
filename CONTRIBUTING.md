# Contributing

Welcome: issues and pull requests in Persian or English.

**Add a company careers page:** edit `jobradar/data/companies.json` and add `name`, `name_fa`, `sector`, `url`. The URL must open (HTTP 200) on the day you add it. Put that date in the pull request.

**Add a job site:** open an issue first. Say whether the site's terms allow automated reading and whether it needs a login. The radar never logs in to a site, never gets around a block, and asks for one page at a time with a pause between requests.

**Code:** run `python -m pytest -q` before you open a pull request. Every score must come with a reason a person can read, in both languages (`rank.py`).
