import re
from bs4 import BeautifulSoup, Comment
import requests
import logging

_log = logging.debug

def tag_visible(element):
    """

    :aim: to filter out unwanted tags from scrapped
    :param element: element from the page
    :return: bool for the filter
    """
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def scrape(url):

    """
    :aim: scrape a web page
    :param url: takes a url as a string
    :return:
    """
    page_response = requests.get(url, timeout=5)
    page_content = BeautifulSoup(page_response.content, "html.parser")
    textContent = []

    #scrapes entire page
    texts = page_content.findAll(text=True) #iterable passed to filter
    visible_texts = filter(tag_visible, texts)
    final_content = " ".join(t.strip() for t in visible_texts)
    all_word_list = re.sub("[^\w]", " ", final_content.strip()).split()

    #scrapes paragraph to be rendered to results page
    temp = page_content.find_all("p")
    for i in range(0, len(temp)):
        paragraphs = page_content.find_all("p")[i].text.strip()
        textContent.append(paragraphs)

    wordList = []
    for i in textContent:
        wordList = wordList + re.sub("[^\w]", " ", i).split() #cleans out symbols

    links = []
    for link in page_content.find_all('a', attrs={'href': re.compile("^https://")}):
        links.append(link.get('href'))

    #Would have used dict(Counter(wordList)) but keys had symbols which weren't allowed in mongodb
    #Plus times constraint to finish project preventing a better approach
    WORDS = {}
    for j in all_word_list:
        if j not in WORDS:
            WORDS[j.lower()] = 1
        else:
            WORDS[j.lower()] += 1

    try:
        title = page_content.title.string
    except AttributeError as e:
        title = ""
        _log(e)

    paragraph_content = " ".join(wordList[:50]) + "..."

    return {

             "word_counts": WORDS,
             "related_links": links,
             "details": paragraph_content,
             "url": url,
             "title": title,
    }

