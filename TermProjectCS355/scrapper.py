import re
from bs4 import BeautifulSoup
import requests


def scrape(url):

    """
    :aim: scrape a web page
    :param url: takes a url as a string
    :return:
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
        wordList = wordList + re.sub("[^\w]", " ", i).split() #cleans out symbols

    links = []
    for link in page_content.find_all('a'):
        links.append(link.get('href'))

    #Would have used dict(Counter(wordList)) but keys had symbols which weren't allowed in mongodb
    #Plus times constraint to finish project preventing a better approach
    WORDS = {}
    for j in wordList:
        if j not in WORDS:
            WORDS[j.lower()] = 1
        else:
            WORDS[j.lower()] += 1

    final_content = " ".join(wordList[:50]) + "..."

    return {

             "word_counts": WORDS,
             "related_links": links,
             "details": final_content,
             "url": url,
             "title": page_content.title.string
    }

