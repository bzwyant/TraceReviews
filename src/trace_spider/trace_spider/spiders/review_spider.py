import scrapy
from scrapy.spiders import CrawlSpider, Request
from scrapy.utils.defer import maybe_deferred_to_future
from twisted.internet.defer import DeferredList

import os
from dotenv import load_dotenv
import json

from pymongo  import ASCENDING, DESCENDING
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


load_dotenv()
atlas_password = os.getenv('ATLAS_PASSWORD')
uri = f"mongodb+srv://bwyant:{atlas_password}@trace.gqna2hn.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
reports_db = client['reports']
course_info_collection = reports_db['courseInfo']

COOKIE = os.getenv('TRACE_SESSION_COOKIE')

class ReviewSpider(CrawlSpider):
    name = "review_spider"
    allowed_domains = ["applyweb.com"]
    start_urls = ["https://applyweb.com"]
    headers = {
        'authority': 'www.applyweb.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'cookie': COOKIE,
        'pragma': 'no-cache',
        'referer': 'https://www.applyweb.com/eval/new/coursereport?sp=70278&sp=5871&sp=148',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'iframe',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }

    def start_requests(self):
        # get the course_reports
        count = 2

        for course_batch in self.get_course_batch(20):
            if count == 0:
                return
            count -= 1
            # print(course_batch)

            # # exit()
            # deferreds = []
            responses = []

            for course in course_batch:
                course_id = course.get("courseId")
                instructor_id = course.get("instructorId")
                term_id = course.get("termId")
                url = f"https://www.applyweb.com/eval/new/showreport?c={course_id}&i={instructor_id}&t={term_id}&r=10&d=true"
                request = Request(
                    url,
                    method='GET',
                    headers=self.headers,
                    callback=self.parse_instructor_report,
                    errback=self.errback_info,
                    meta={'dont_merge_cookies': True}
                )

                yield request

            #     deferred = self.crawler.engine.download(request)
            #     deferreds.append(deferred)

            # responses = await maybe_deferred_to_future(DeferredList(deferreds))
            # yield {"hi": "test"}

    
    def get_course_batch(self, batch_size: int):
        last_id_seen = 0

        while last_id_seen != -1:
            cursor = course_info_collection.find({"courseId": {"$gt": last_id_seen}}).sort('courseId', ASCENDING).limit(batch_size)
            result = list(cursor)
            
            # Convert ObjectId values to strings in the result
            for doc in result:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])

            last_id_seen = result[-1].get("courseId", -1) if result else -1
            # print(last_id_seen)
            # json_result = json.dumps(result, indent=2)
            # yield json_result

            yield result

    def parse_instructor_report(self, response):
        self.logger.info(response)

    def errback_info(self, failure):
        # log all failures
        self.logger.error(f"\n\n{repr(failure)}\n\n")


if __name__ == "__main__":
    spider = ReviewSpider()

    batch_limit = 10
    for batch_json in spider.get_course_batch(batch_size=4):
        print(batch_json)
        batch_limit -= 1
        if batch_limit == 0:
            break