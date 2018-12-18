from flask import Flask
from flask import render_template
from flask import request
from db_manager import DBManager
from json2html import *
from pymongo import errors
import logging

_log = logging

app = Flask(__name__)

db_handler = DBManager()

@app.route('/')
def search_engine():
    """

    :aim: The search engine landing page
    :return: search engine
    """
    return render_template('index.html')

@app.route('/result', methods = ['GET', 'POST'])
def handle_data():
    """

    :aim: Shows search result page. Checks redis first before mongodb if there's more
    :return: search result page
    """
    try:

        import time
        start = time.time()
        projectpath = request.form['projectFilepath']

        final_result = {}
        results = db_handler.redis_get_all(projectpath)
        if results:
            for j in results:
                final_result[j] = results.get(j)

            results = db_handler.query_mongo(projectpath.lower())
            for j in results:
                if results.get(j) not in final_result.values():
                    final_result[j] = results.get(j)
        else:
            final_result = db_handler.query_mongo(projectpath.lower())

        end = time.time()
        if final_result is None:
            final_result = "Sorry we could not find what you're searching for"
            db_handler.redis_set(projectpath, final_result)
            string = "We have 0 result(s) (" + str(round(end - start, 4) % 60) + " seconds)"
        else:
            db_handler.redis_set(projectpath, final_result)
            string = "We have " + str(len(final_result)) + " result(s) (" + str(round(end - start, 4) % 60) + " seconds)"

        return render_template("result.html", result=final_result, timer=string)
    except errors.CursorNotFound as e:
        _log.debug(e)
        return "Admin, please reset the database before searching"


@app.route("/admin_result")
def get_data():
    """

    :aim: show info in the database
    :return: result of the database rendered to /admin_result
    """
    result = db_handler.mongo_get_all()
    return render_template("admin_result.html", result=result)


@app.route("/admin", methods = ['GET', 'POST'])
def admin_page():
    """

    :aim: Directs to admin page
    :return: Admin page
    """
    return render_template("admin.html")


@app.route("/admin_results", methods = ['GET', 'POST'])
def add_url():
    """

    :aim: add page to be indexed
    :return: admin page
    """
    try:
        url = request.form['projectFilepath']
        db_handler.add_url(url)
        mssg = "Page info has sucessfully been stored"
        return render_template("admin.html" , mssg=mssg)
    except errors.InvalidURI:
        mssg = "There was an error in adding your page, try again later!"
        return render_template("admin.html" , mssg=mssg)


@app.route("/history", methods = ['GET', 'POST'])
def search_history():
    """

    :aim: shows history page
    :return: history page
    """
    history = db_handler.get_cached_history()
    return render_template("history.html", history=history)


@app.route("/admin_reset", methods = ['GET', 'POST'])
def reset_db():
    """
    :aim: stored in database
    :return: admin page
    """
    db_handler.reset_db()
    return render_template("admin.html")


if __name__ == '__main__':
   app.run()

