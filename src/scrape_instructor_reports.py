#!/usr/bin/python

import httpx
import asyncio
from time import time
from dotenv import load_dotenv
import os
import requests
from util.html_parser import parse_instructor_summary
from util.mongo_tools import create_async_client, get_course_info_batch
import json
from math import floor


# print(response.text)


async def get_instructor_comments(client, url, headers):
    # async with client:
    r = await client.get(url=url, headers=headers)
    # print(r.text)
    # print(r.status_code)
    instructor_comments = parse_instructor_summary(r.text)
    return instructor_comments


async def main():
    # REQUEST INFO
    load_dotenv()
    COOKIE = os.getenv("TRACE_SESSION_COOKIE")

    # course_id = 84119
    # instructor_id = 6939
    # term_id = 168
    instructor_report_url = lambda course_id, instructor_id, term_id: f"https://www.applyweb.com/eval/new/showreport?c={course_id}&i={instructor_id}&t={term_id}&r=10&d=true"

    payload = {}
    headers = {
        'authority': 'www.applyweb.com',
        # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        # 'accept-language': 'en-US,en;q=0.9',
        # 'cache-control': 'no-cache',
        'cookie': COOKIE,
        # 'pragma': 'no-cache',
        # 'referer': 'https://www.applyweb.com/eval/new/coursereport?sp=84144&sp=6719&sp=168',
        # 'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': '"macOS"',
        # 'sec-fetch-dest': 'iframe',
        # 'sec-fetch-mode': 'navigate',
        # 'sec-fetch-site': 'same-origin',
        # 'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    # DB info
    atlas_password = os.getenv('ATLAS_PASSWORD')
    uri = f"mongodb+srv://bwyant:{atlas_password}@trace.gqna2hn.mongodb.net/?retryWrites=true&w=majority"
    database = 'reports'
    collection = 'courseInfo'

    mongo_client = create_async_client(uri=uri)

    async with httpx.AsyncClient() as client:
        batch_limit = 10
        batch_size = 20

        #NOTE: Not sure this needs to be async but can just switch to using create_client to make it not async retrieval
        #NOTE: @myself get_course_info_batch is a GENERATOR (so you loop through it) 
        async for course_info_batch in get_course_info_batch(mongo_client, database, collection, batch_size):
            tasks = []
            # print(json.dumps(batch, indent=2), '\n')
            for course_info in course_info_batch:
                course_url = instructor_report_url(course_info['courseId'], course_info['instructorId'], course_info['termId'])
                tasks.append(asyncio.ensure_future(get_instructor_comments(client, course_url, headers)))

            batch_comments = await asyncio.gather(*tasks)
            for review in batch_comments:
                # print(review["comments"])
                print(review["professor"])

            batch_limit -= 1
            if batch_limit == 0:
                break

    # asyncio.run(get_instructor_comments(url, headers))


if __name__ == "__main__":
    start = time()
    asyncio.run(main())
    stop = time()

    seconds_elapsed = stop - start
    print(f"time: {floor(seconds_elapsed / 60)} min {round(seconds_elapsed // 60)}s")
    