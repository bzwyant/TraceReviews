# TraceReviews

## Scraping Reviews

scripts/scrape_courses.sh will place all the metadata of each course ever listed into a mongodb 

This is done using a scrapy spider which I (@bzwyant) moved away from afterwards. I switched over to using httpx and asyncio to scrape the actual comments from reviews

## Future Tasks

#### - Build an API to query professors and courses
#### - Rank professors based on reviews (the initial goal of this project)

## Useful Resources
#### Python Async
Async requests
- [Asyncio and coroutines explained](https://bbc.github.io/cloudfit-public-docs/asyncio/asyncio-part-1)


MongoDB
- [Async w/ Mongodb using Motor](https://gist.github.com/anand2312/840aeb3e98c3d7dbb3db8b757c1a7ace)