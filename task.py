"""Template robot with Python."""

import logging
import re
import sqlite3
from time import sleep

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files

browser_lib =  Selenium(auto_close=False)
excel_lib = Files()

con = sqlite3.connect("rotten.db")
cur = con.cursor()

ROTTENTTOMATOES_URL = 'https://www.rottentomatoes.com/'
MOVIES_EXCEL_FILE = 'movies.xlsx'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')


def remove_punctuations(string):
    pattern = r'[\"\',]'
    return re.sub(pattern, '', string)


def open_rotten_tomatoes_website():
    browser_lib.open_browser(ROTTENTTOMATOES_URL,"firefox")


def create_table_movies():
    create_table_sql = """
        CREATE TABLE movies(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_name TEXT NOT NULL,
            tomatometer_score TEXT,
            audience_score TEXT,
            tomatometer_state TEXT,
            storyline TEXT,
            rating TEXT,
            genres TEXT,
            review_1 TEXT,
            review_2 TEXT,
            review_3 TEXT,
            review_4 TEXT,
            review_5 TEXT,
            status TEXT
        )
    """
    cur.execute(create_table_sql)


def search_and_extract_movies():
    excel_lib.open_workbook(MOVIES_EXCEL_FILE)
    worksheet = excel_lib.read_worksheet_as_table(header=True)
    excel_lib.close_workbook()

    for movie in worksheet:
        logging.info(movie['Movie']) 

        if movie["Movie"]== "":
            break
        search_movie(movie['Movie'])


def search_movie(movie):
    get_movie = movie
    sleep(4)
    browser_lib.wait_until_element_is_visible('//*[@id="header-main"]/search-algolia/search-algolia-controls/input')
    browser_lib.input_text('//*[@id="header-main"]/search-algolia/search-algolia-controls/input', get_movie)
    sleep(1)
    browser_lib.click_link('//html/body/div[3]/rt-header/search-algolia/search-algolia-controls/a')
    sleep(2)
    browser_lib.wait_until_element_is_visible('//html/body/div[3]/main/div[1]/div/section[1]/div/nav/ul/li[3]')

    # If popup arises
    popup = browser_lib.get_webelements('/div[@css="dgEhJe6g"]')
    if popup:
        browser_lib.click_button('/html/body/div[5]/div/div[1]/div/div[3]/span[1]/button')
    sleep(0.577)
    filter_movie(get_movie)


def filter_movie(movie):
    # Filter by movie
    browser_lib.wait_until_element_is_visible('//li[@data-filter="movie"]')
    movie_list = browser_lib.get_webelement('//li[@data-filter="movie"]')
    browser_lib.click_element(movie_list)
    goto_searched_movie(movie)


def goto_searched_movie(movie):
    # Get movies
    given_movie = movie.strip()
    browser_lib.wait_until_page_contains_element('//ul[@slot="list"]/search-page-media-row/a[@data-qa="info-name"]')
    titles = browser_lib.get_webelements('//ul[@slot="list"]/search-page-media-row/a[@data-qa="info-name"]')

    latest_movie_title = None

    for title in titles:
        movie_title = browser_lib.get_text(title)
        movie_title_new = movie_title.strip()
        given_movie = given_movie.strip()

        if movie_title_new == given_movie:
            latest_movie_title = movie_title
            link = browser_lib.get_element_attribute(title, 'href')
            logging.info(link)
            logging.info(latest_movie_title)
            break

    # Extract data if movie found
    if latest_movie_title:
        extract_movie_data(link)

    if not latest_movie_title:
        movie_data = {
            "movie_name": movie,
            "tomatometer_score": "N/A",
            "audience_score": "N/A",
            "tomatometer_state": "N/A",
            "storyline": "N/A",
            "rating": "N/A",
            "genres": "N/A",
            "review_1": "N/A",
            "review_2": "N/A",
            "review_3": "N/A",
            "review_4": "N/A",
            "review_5": "N/A",
            "status": "No exact match found"
        }
        insert_into_table(movie_data)


def extract_movie_data(link):
    # navigate to movie page
    browser_lib.go_to(link)
    sleep(5)
    movie_name = browser_lib.get_text("//h1[@class='title']")
    tomatometer_score = browser_lib.get_element_attribute('//score-board[@data-qa="score-panel"]', 'tomatometerscore')
    audience_score = browser_lib.get_element_attribute('//score-board[@data-qa="score-panel"]', 'audiencescore')
    rating = browser_lib.get_element_attribute('//score-board[@data-qa="score-panel"]', 'rating')
    tomatometer_state = browser_lib.get_element_attribute('//score-board[@data-qa="score-panel"]', 'tomatometerstate')


    browser_lib.wait_until_element_is_visible('id:movie-info')
    storyline = browser_lib.get_text('//p[@data-qa="movie-info-synopsis"]')
    genres = browser_lib.get_text('//*[@id="info"]/li[1]/p/span')

    browser_lib.wait_until_element_is_visible('id:critics-reviews')
    reviews = browser_lib.find_elements('//review-speech-balloon[@data-qa="critic-review"]')
    review_1 = reviews[0].text if len(reviews) >= 1 else "N/A"
    review_2 = reviews[1].text if len(reviews) >= 2 else "N/A"
    review_3 = reviews[2].text if len(reviews) >= 3 else "N/A"
    review_4 = reviews[3].text if len(reviews) >= 4 else "N/A"
    review_5 = reviews[4].text if len(reviews) >= 5 else "N/A"
    
    # Remove punctuations from review text
    review_1 = remove_punctuations(review_1)
    review_2 = remove_punctuations(review_2)
    review_3 = remove_punctuations(review_3)
    review_4 = remove_punctuations(review_4)
    review_5 = remove_punctuations(review_5)
    status = "Success"

    movie_data = {
        "movie_name": movie_name,
        "tomatometer_score": tomatometer_score,
        "audience_score": audience_score,
        "tomatometer_state": tomatometer_state,
        "storyline": storyline,
        "rating": rating,
        "genres": genres,
        "review_1": review_1,
        "review_2": review_2,
        "review_3": review_3,
        "review_4": review_4,
        "review_5": review_5,
        "status": status
    }
    logging.info("Inserting into table.")
    insert_into_table(movie_data)


def insert_into_table(movie_data):
    insert_sql = """
        INSERT INTO movies (
            movie_name, 
            tomatometer_score, 
            audience_score, 
            tomatometer_state, 
            storyline, 
            rating, 
            genres, 
            review_1, 
            review_2, 
            review_3, 
            review_4, 
            review_5, 
            status
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur.execute(insert_sql,(
        movie_data["movie_name"], 
        movie_data["tomatometer_score"], 
        movie_data["audience_score"], 
        movie_data["tomatometer_state"], 
        movie_data["storyline"], 
        movie_data["rating"], 
        movie_data["genres"], 
        movie_data["review_1"], 
        movie_data["review_2"], 
        movie_data["review_3"], 
        movie_data["review_4"], 
        movie_data["review_5"], 
        movie_data["status"]
    ))
    con.commit()
    data = cur.execute("Select * from movies")
    logging.info(data.fetchall())


def main():
    open_rotten_tomatoes_website()
    try:
        create_table_movies()
    except:
        logging.info("Database already exists")

    search_and_extract_movies()
    cur.close()
    con.close()
    browser_lib.close_browser()

if __name__=="__main__":
    main()
