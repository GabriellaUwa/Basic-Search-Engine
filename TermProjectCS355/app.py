from flask import Flask
from flask import render_template
from flask import request
from redis import Redis, StrictRedis
from scrapper import scrape
import urllib.request, xmltodict, json
from io import BytesIO
from scrapper import scrape

app = Flask(__name__)
URLS = [
    "https://en.wikipedia.org/wiki/Main_Page"
]

redis = StrictRedis()
default = scrape(URLS[0])

@app.route('/')
def search_engine():
    """
    Ensures things are already in the cache before user starts to query
    :return:
    """
    #popultate_redis()
    return render_template('index.html')

@app.route('/result', methods = ['GET', 'POST'])
def handle_data():
    """
    This takes in the query and gives response based on if something similar is in the DB
    :return:
    """

    projectpath = request.form['projectFilepath']


    return projectpath #return the link to the search engine stuff... nice! as html containing content!

def popultate_redis():

    """
    Results will be stored as a key to Map a dictionary of queries mapped to a page object model
    :return: None
    """

    #populate here with any necessary info

    #pages = [pages]
    #redis.set('default', json.dumps(default))

    #print(redis.get('default'))
    #reply = json.loads(redis.execute_command('JSON.GET', 'object'))
    pass


if __name__ == '__main__':
   app.run()
