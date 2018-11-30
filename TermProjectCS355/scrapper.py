import re
from bs4 import BeautifulSoup
import requests, logging

logger = logging

def scrape(url):

    """

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
    WORDS = {}
    for j in wordList:
        if j not in WORDS:
            WORDS[j] = 1
        else:
            WORDS[j] += 1

    final_content = " ".join(wordList[:30]) + "..."

    return { "word_counts": WORDS, "related_links": links, "details": final_content, "url": url}
