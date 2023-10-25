# scrapy
import scrapy
from scrapy.spiders import CrawlSpider
# util
import json
import os
from dotenv import load_dotenv
# database
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


class CourseSpider(CrawlSpider):
    name = 'course_spider'
    allowed_domains = ['applyweb.com']
    start_url = 'https://www.applyweb.com/eval/new/reportbrowser/evaluatedCourses'
    headers = {
        'authority': 'www.applyweb.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/json;charset=UTF-8',
        'cookie': COOKIE,
        'origin': 'https://www.applyweb.com',
        'pragma': 'no-cache',
        'referer': 'https://www.applyweb.com/eval/resources/js/reportbrowser/reportbrowser.html',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    rpp = 2000

    # custom_settings = {
    #     'CONCURRENT_REQUESTS': 100
    # }

    handle_httpstatus_list = [401]

    def start_requests(self):
        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            self.logger.info("\n\nPinged your deployment. You successfully connected to MongoDB!\n")
        except Exception as e:
            self.logger.error(f"\n\n{e}\nCould not connect to mongodb Atlas. EXITING...\n")
            return

        yield scrapy.Request(
            self.start_url,
            method='POST',
            headers=self.headers,
            body=json.dumps({"page": 1, "rpp": 1, "excludeTA": False, "sort": None}),
            callback=self.scrape_courses,
            errback=self.errback_info,
            meta={'dont_merge_cookies': True}
        )
    
    def scrape_courses(self, response):
        try:
            data = json.loads(response.text)
            total_num_courses = int(data.get('total'))
            self.logger.info(f"\n\n\nTOTAL NUMBER OF COURSES: {total_num_courses}\n\n")
        except:
            self.logger.error("\n\nCould not get total number of courses\n")

        try:
            pages_to_scrape = (total_num_courses // self.rpp) + 1
            for page in range(1, pages_to_scrape + 1):
                self.logger.info(f"\nScraping page {page} with rpp {self.rpp}")
                yield scrapy.Request(
                    self.start_url,
                    method='POST',
                    headers=self.headers,
                    body=json.dumps({"page": page, "rpp": self.rpp, "excludeTA": False, "sort": None}),
                    callback=self.parse_courses,
                    errback=self.errback_info,
                    meta={'dont_merge_cookies': True}
                )
        except:
            self.logger.error(f"\n\nCaught exception in scrape_courses: {response.text}\n")


    def parse_courses(self, response):
        # Uncomment lines below to debug
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        # try:
        #     data = json.loads(response.text)
        #     courses = data.get('data')

        #     results = course_info_collection.insert_many(courses)

        #     with open('inserted_courses.json') as file:
        #         file.write(json.dumps(results))

        #     yield courses
        try:
            self.logger.info("WHATTTT")
            
        # Catch 401 errors
        except Exception:
            self.logger.error(f"\n\nERROR WHILE PARSING COURSES: {response.text}\n")


    def errback_info(self, failure):
        # log all failures
        self.logger.error(f"\n\n{repr(failure)}\n\n")
