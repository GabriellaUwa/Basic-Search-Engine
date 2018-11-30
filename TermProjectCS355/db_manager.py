from redis import Redis
from pymongo import MongoClient
from scrapper import scrape
import json, time, logging

log = logging.debug


class DBManager():


    #Mongo Database Initialization
    client = MongoClient('mongodb://localhost:27017/')

    #Search Database
    db = client["searchDB"]

    #All Collections
    word_collection = db["wordIndex"]
    page_collection = db["pageIndex"]
    page_word_collection = db["pageWord"]
    page_content_collection = db["pageContent"]

    #Redis Database
    redis = Redis()

    URLS = [
        "https://en.wikipedia.org/wiki/Main_Page",
        "https://en.wikipedia.org/wiki/Beyonc%C3%A9",
        "https://www.qc.cuny.edu/about/Pages/default.aspx"
    ]

    related_links = []


    def setup_collections(self, urls=URLS):
        """

        :aim:
        :return:
        """
        global related_links
        words = []  # for word_collection
        pages = []  # for page_collection
        page_word = []  # for page_word_collection
        page_content = []  # for page_content_collection

        page_index = 1

        for i in urls:
            temp = scrape(i)
            word_index = 1

            pages.append({str(page_index): i})  # maps index: urls

            word_counts = temp.get("word_counts")

            for key in word_counts.keys():  # maps index: word
                words.append({str(word_index): key})
                word_index += 1

            page_word.append({str(page_index): word_counts})  # maps page_index: {word: count}
            page_content.append({str(page_index): temp.get("details")})  # maps {page_index: content}
            page_index += 1

            related_links = related_links + temp.get("related_links")


    def more_link_index(self):
        """

        :aim: The more people search the more things will get indexed. Hence this function call
        :return: None
        """
        self.setup_collections(related_links)

    def redis_set(self,query, page_info):
        """

        :aim: Sets query to page_info in redis for 24 hours, iff it is not already stored
        :param query: String of a Query
        :param page_info: Dictionary of page info
        :return: None
        """
        self.redis.set(query, json.dumps(page_info), ex= time.time() + 86400, nx=True)

    def redis_get_all(self):

        """

        :return: queries and their page info
        """
        queries = {}
        keys = self.redis.keys('*')
        for key in keys:
            queries[key.decode("utf-8")] = json.loads(self.redis.get(key).decode("utf-8"))

        return queries

    def add_url(self, url):
        self.URLS.append(url)