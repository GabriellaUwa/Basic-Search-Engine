import re
from collections import Counter
from bs4 import BeautifulSoup
import requests

def scrape(url):

    """

    :param url: takes a url as a string
    :return: a map of its page content as a Counter Object and list of related links
    """

    page_response = requests.get(url, timeout=5)
    page_content = BeautifulSoup(page_response.content, "html.parser")
    textContent = []

    temp = page_content.find_all("p")
    for i in range(0, len(temp)):
        paragraphs = page_content.find_all("p")[i].text.strip()
        textContent.append(paragraphs)

    wordList = []
    for i in textContent:
        wordList = wordList + re.sub("[^\w]", " ", i).split()

    links = []
    for link in page_content.find_all('a'):
        links.append(link.get('href'))

    WORDS = {}
    for j in wordList:
        if j not in WORDS:
            WORDS[j] = 1
        else:
            WORDS[j] += 1

    return { "content": WORDS, "links": links }
