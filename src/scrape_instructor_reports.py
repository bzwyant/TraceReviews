#!/usr/bin/python

import httpx
import asyncio
from time import time
from dotenv import load_dotenv
import os
import requests
from util.html_parser import parse_instructor_summary
from util.mongo_tools import (
    create_client,
    create_async_client, 
    aget_course_info_batch, 
    get_collection,
    ainsert_many
)
import json
from math import floor


# print(response.text)


async def get_instructor_comments(client: httpx.AsyncClient, url, headers):
    # async with client:
    r = await client.get(url=url, headers=headers, timeout=30.0)
    # print(r.text)
    if r.status_code != 200:
        print(r.status_code)
        raise Exception("Cannot connect")
    instructor_comments = parse_instructor_summary(r.text)
    return instructor_comments


async def main():
    # REQUEST INFO
    load_dotenv()
    COOKIE = os.getenv("TRACE_SESSION_COOKIE")

    instructor_report_url = lambda course_id, instructor_id, term_id: f"https://www.applyweb.com/eval/new/showreport?c={course_id}&i={instructor_id}&t={term_id}&r=10&d=true"

    payload = {}
    headers = {
        'authority': 'www.applyweb.com',
        'cookie': COOKIE,
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    # DB info
    course_info_client_uri = os.getenv('COURSE_INFO_CLIENT_URI')
    course_info_db_name = 'reports'
    course_info_collection_name = 'courseInfo'

    mongo_ci_client = create_async_client(uri=course_info_client_uri)
    course_info_collection = get_collection(client=mongo_ci_client, database=course_info_db_name, collection=course_info_collection_name)

    course_reviews_client_uri = os.getenv('COURSE_REVIEWS_CLIENT_URI')
    course_reviews_db_name = 'Northeastern'
    course_reviews_collection_name = 'CourseReviews'

    mongo_cr_client = create_async_client(uri=course_reviews_client_uri)
    course_reviews_collection = get_collection(mongo_cr_client, database=course_reviews_db_name, collection=course_reviews_collection_name)

    num_scraped = 0
    async with httpx.AsyncClient() as client:
        # batch_limit = 10
        batch_size = 500

        #NOTE: Not sure this needs to be async but can just switch to using create_client to make it not async retrieval
        #NOTE: @myself get_course_info_batch is a GENERATOR (so you loop through it)
        async for course_info_batch in aget_course_info_batch(course_info_collection, batch_size):
            tasks = []
            # print(json.dumps(batch, indent=2), '\n')
            for course_info in course_info_batch:
                course_url = instructor_report_url(course_info['courseId'], course_info['instructorId'], course_info['termId'])
                tasks.append(asyncio.ensure_future(get_instructor_comments(client, course_url, headers)))

            batch_review_maps = await asyncio.gather(*tasks)

            to_insert = []
            for course_info_dict, review_map in zip(course_info_batch, batch_review_maps):
                to_insert.append({
                    "courseId": course_info_dict["courseId"],
                    "instructorId": course_info_dict["instructorId"],
                    "termId": course_info_dict["termId"],
                    "instructorFirstName": course_info_dict["instructorFirstName"],
                    "instructorMiddleName": course_info_dict["instructorMiddleName"],
                    "instructorLastName": course_info_dict["instructorLastName"],
                    "departmentName": course_info_dict["departmentName"],
                    "subject": course_info_dict["subject"],
                    "number": course_info_dict["number"],
                    "termTitle": course_info_dict["termTitle"],
                    "comments": review_map["comments"]
                })
            result = await ainsert_many(collection=course_reviews_collection, to_insert=to_insert)

            num_scraped += len(batch_review_maps)
            if num_scraped % 1000 == 0:
                print(num_scraped)

            # batch_limit -= 1
            # num_batches += 1
            # if batch_limit == 0:
            #     break

    return num_scraped


if __name__ == "__main__":
    start = time()
    scraped_count = asyncio.run(main())
    stop = time()

    seconds_elapsed = stop - start
    print(f"{seconds_elapsed} seconds to scrape {scraped_count} reviews")