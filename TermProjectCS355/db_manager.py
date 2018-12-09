from redis import Redis
from flask_pymongo import MongoClient
from scrapper import scrape
import json, time, logging, re, os
import urllib.parse as urlparse
import configparser

log = logging.debug


class DBManager():

    #clean up later
    url = urlparse.urlparse("redis://h:pf1961dc8a32a43730a9db4190e6c504bb5a96b0b273a3a3d34c19dd3426d0804@ec2-34-225-229-4.compute-1.amazonaws.com:59769")
    redis = Redis(host=url.hostname, port=url.port, password=url.password)
    mongo_client = MongoClient("mongodb://heroku_b629lqd4:eaula0va2orvkjrko8pmsptkg4@ds227853.mlab.com:27853/heroku_b629lqd4")

    #MongoDB Sandbox
    db = mongo_client["heroku_b629lqd4"]

    #All Collections
    word_collection = db["wordIndex"]
    page_collection = db["pageIndex"]
    page_word_collection = db["pageWord"]
    page_content_collection = db["pageContent"]
    by_title = db["searchTitle"]
    page_title = db["page_title"]


    URLS = [
        "https://en.wikipedia.org/wiki/Main_Page",
        "https://en.wikipedia.org/wiki/Beyonc%C3%A9",
        "https://www.qc.cuny.edu/about/Pages/default.aspx"
    ]

    related_links = []
    adder = 1

    def setup_collections(self, urls=URLS):
        """

        :aim: populates Mongodb with searchable information
        :return: None
        """
        global related_links
        pages = []  # for page_collection
        page_word = []  # for page_word_collection
        page_content = []  # for page_content_collection
        title = []
        page_title = []

        page_index = 1
        if len(urls) == 1:
            page_index= self.page_word_collection.find({}).count() + 1
        for i in urls:
            temp = scrape(i)

            pages.append({str(page_index): i})  # maps index: urls

            word_counts = temp.get("word_counts")


            page_word.append({str(page_index): word_counts})  # maps page_index: {word: count}
            page_content.append({str(page_index): temp.get("details")})  # maps {page_index: content}

            title.append({temp.get("title"): [i, temp.get("details")]})

            page_title.append({str(page_index): temp.get("title")})
            page_index += 1


        self.page_collection.insert_many(pages)
        self.page_word_collection.insert_many(page_word)
        self.page_content_collection.insert_many(page_content)
        self.by_title.insert_many(title)
        self.page_title.insert_many(page_title)
        #related_links = related_links + temp.get("related_links")

    def more_link_index(self):
        """

        :aim: The more people search the more things will get indexed. Hence this function call
        :return: None
        """
        #self.setup_collections(related_links)
        pass


    def redis_set(self,query, page_info):
        """

        :aim: Sets query to page_info in redis for 24 hours, iff it is not already stored
        :param query: String of a Query
        :param page_info: Dictionary of page info
        :return: None
        """
        self.redis.set(query, json.dumps(page_info), ex= int(time.time()) + 86400, nx=True)


    def redis_get_all(self, query):
        """

        :aim: For faster search. Checks redis before hitting mongodb
        :return: queries and their page info
        """
        queries = {}
        s_query = re.sub("[^\w]", " ", query).split()

        keys = self.redis.keys('*')
        for key in keys:
            for q in s_query:
                if q in key.decode("utf-8"):
                    new_dict = json.loads(self.redis.get(key).decode("utf-8"))
                    if new_dict:
                        for k,v in new_dict.items():
                            queries[k] = v
        if queries != {}:
            return queries

    def get_cached_history(self):
        """

        :aim: To get search history for admin user
        :return: Search history, which are stored as keys in redis
        """

        keys = self.redis.keys('*')
        history = []
        for key in keys:
            history.append(key.decode('utf-8'))

        return history

    def clear_cached(self):
        """

        :aim: clear redis history
        :return: None
        """
        keys = self.get_cached_history()
        for key in keys:
            self.redis.delete(key)

    def mongo_get_all(self):
        """

        :aim: Show admin all data stored in the database
        :return:
        """
        pages = self.page_collection.find({}, {'_id': False})
        page_word = self.page_word_collection.find({}, {'_id': False})
        page_content = self.page_content_collection.find({}, {'_id': False})
        title = self.by_title.find({}, {'_id': False})
        page_title = self.page_title.find({}, {'_id': False})

        return {
                "page_indexes": [p for p in pages],
                "page-word"   : [pw for pw in page_word],
                "page-content": [pc for pc in page_content],
                "title"       : [t for t in title],
                "page-title"  : [pt for pt in page_title]

        }


    def query_mongo(self, query):
        """

        :aim: Use mongo aggregation to get desired pages. Search is done by title and word occurrence
        :note: Run time may be O(n^4) but each level of iteration is small
        :param query:  string of words
        :return:
        """
        results = {}
        wordList = re.sub("[^\w]", " ", query).split()
        titles = self.by_title.find({}, {'_id': False})


        #Search
        for title in titles:
            for j in title:
                for k in wordList:
                    if k.lower() in j.lower():
                        if title.get(j)[1] not in results.values():
                            results[title.get(j)[0]] = [j, title.get(j)[1]]

        page_word = self.page_word_collection.find({}, {'_id': False})
        pw = [pw for pw in page_word]

        result_pages = []

        for word in wordList:
            for j in pw:
                for k,v in j.items():
                    for word in wordList:
                        if word in v.keys() and v.get(word) > 10 and k not in result_pages:
                           result_pages.append(k)

            pages = self.page_collection.find({}, {'_id': False})
            page_content = self.page_content_collection.find({}, {'_id': False})
            p_content = [pc for pc in page_content]

            page_title = self.page_title.find({}, {'_id': False})
            p_title = [pt for pt in page_title]

            for page in result_pages:
                for p in pages:
                    if page in p:
                        for content in p_content:
                            for pt in p_title:
                                if page in content and p.get(page) not in results.values():
                                    results[p.get(page)] = [pt.get(page),content.get(page)]
                                elif page in content and p.get(page) in results.values():
                                    results[p.get(page)+str(self.adder)] = [pt.get(page).strip(),content.get(page)]
        if results != {}:
            return results


    def add_url(self, url):
        """

        :param url: adding new page url to be stored into DB
        :return:
        """
        self.URLS.append(url)
        self.setup_collections([url])

    def reset_db(self):
        """
        :aim: restores db's to default and clears cache
        :return: None
        """
        self.page_collection.delete_many({})
        self.page_word_collection.delete_many({})
        self.page_content_collection.delete_many({})
        self.by_title.delete_many({})
        self.page_title.delete_many({})
        self.clear_cached()

        # if reset db, run below script

    def populate(self):
        """
        :aim: puts page info into database
        :return:
        """
        self.setup_collections()
