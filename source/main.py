#!usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import sqlite3
import time

import signal, os
import os.path
import logging

from selenium.webdriver import Chrome
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.alert import Alert


#DATABASE Diagram
# CREATE TABLE event (
#   company TEXT NOT NULL,
#   date    TEXT NOT NULL,
#   image   TEXT NOT NULL,
#   title   TEXT NOT NULL,
#   content TEXT NOT NULL
#)

URL_1 = 'https://www.burgerking.co.kr/#/home'
URL_2 = 'https://www.mcdonalds.co.kr/kor/promotion/list.do'
URL_3 = 'https://www.starbucks.co.kr/whats_new/store_event_list.do'
URL_4 = 'https://www.bbq.co.kr/event/eventList.asp?event=OPEN'
URL_5 = 'https://www.caffe-pascucci.co.kr/event/eventList.asp'
URL_6 = 'https://www.ediya.com/contents/event.html?tb_name=event'
URL_7 = 'https://www.pizzahut.co.kr'


def connect_sqlite3(db_name):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, db_name)
    conn = sqlite3.connect(db_path)
    print("Opened database successfully")
    cur = conn.cursor()
    return conn, cur


def insert_event_list(conn, cur, company, date, image, title, content):
    if select_event_from_table(cur, title):
        return 0
    else:
        requests.post("http://155.230.52.58:26287/event", params={'company':company, 'date':date, 'image':image, 'title':title, 'content':content})
        query = "INSERT INTO event (company, date, image, title, content) VALUES ('" + company + "', '" + date + "', '" + image + "', '" + title + "', '" + content + "')"
        cur.execute(query)
        conn.commit()
        return 1


def select_event_from_table(cur, title):
    cur.execute("SELECT * FROM event WHERE title IS '" + title + "'")
    rows = cur.fetchone()
    if rows:
        return 1
    else:
        return 0


def clean_up(conn, cur):
    cur.close()
    conn.close()


def get_bk_event(conn, cur):
    company = "burger king"
    driver = Chrome()
    driver.get(URL_1)

    # access event page
    event_page = driver.find_element_by_xpath("//*[@id=\"app\"]/div/div[1]/div/div/div[2]/ul/li[3]/button")
    event_page.click()
    event_page = driver.find_element_by_xpath("//*[@id=\"app\"]/div/div[1]/div/div/div[2]/ul/li[3]/ul/li[1]/a/span")
    event_page.click()

    driver.implicitly_wait(100)
    event_1 = driver.find_element_by_xpath("//*[@id=\"app\"]/div/div[3]/div[2]/div/div[2]/ul/li[1]/button/span/img")
    event_1.click()
    driver.back()

    xpath_front = "//*[@id=\"app\"]/div/div[3]/div[2]/div/div[2]/ul/li["
    xpath_rear = "]/button/span/img"
    for i in range(1, 15):
        driver.implicitly_wait(100)
        xpath = xpath_front + str(i) + xpath_rear
        event = driver.find_element_by_xpath(xpath)

        image = event.get_attribute("src")
        event.click()
        time.sleep(2)

        title_loc = driver.find_element_by_xpath("//*[@id=\"app\"]/div/div[3]/div[2]/div/div[2]/div[1]/h4")
        title = title_loc.text

        date_loc = driver.find_element_by_xpath("//*[@id=\"app\"]/div/div[3]/div[2]/div/div[2]/div[1]/p")
        date = date_loc.text

        content_loc = driver.find_element_by_xpath("//*[@id=\"app\"]/div/div[3]/div[2]/div/div[2]/div[2]/div[1]/p")
        content = content_loc.text

        if insert_event_list(conn, cur, company, date, image, title, content):
            message = title + ' inserted in db' + '\n'
            print(message)

        driver.back()

    driver.close()


def get_md_event(conn,cur):
    company = "mcdonalds"
    driver = Chrome()
    driver.get(URL_2)

    xpath_front = "//*[@id=\"promotionList\"]/li["
    xpath_rear = "]"

    for i in range(1, 6):
        driver.implicitly_wait(100)
        xpath = xpath_front + str(i) + xpath_rear
        event = driver.find_element_by_xpath(xpath)

        image_loc = driver.find_element_by_xpath("//*[@id=\"promotionList\"]/li["+str(i)+"]/a/div[1]/img")
        image = image_loc.get_attribute('src')
        event.click()
        time.sleep(2)

        title_loc = driver.find_element_by_xpath("//*[@id=\"container\"]/div[1]/div[1]/div[2]/div/div/div[1]/h2")
        title = title_loc.text
        title = title.replace('\n','')

        date_loc = driver.find_element_by_xpath("//*[@id=\"container\"]/div[1]/div[1]/div[2]/div/div/div[1]/span/em[1]")
        date = date_loc.text
        date = date.replace('\n','')
        date = date.replace('등록일 :','')

        content_loc = driver.find_element_by_xpath("//*[@id=\"container\"]/div[1]/div[1]/div[2]/div/div/article/div[1]/img")
        content = content_loc.get_attribute('src')

        if insert_event_list(conn, cur, company, date, image, title, content):
            message = title + ' inserted in db' + '\n'
            print(message)

        driver.back()

    driver.close()


def get_sb_event(conn, cur):
    company = "starbucks"
    driver = Chrome()
    driver.get(URL_3)

    driver.implicitly_wait(100)

    xpath_front = "//*[@id=\"lsmBox\"]/li["
    xpath_rear = "]"

    for i in range(1, 5):
        xpath = xpath_front + str(i) + xpath_rear

        image = driver.find_element_by_xpath(xpath + "/dl/dt/a/img").get_attribute("src")
        title = driver.find_element_by_xpath(xpath + "/dl/dd/h4").text
        title = title.split('2')[0]
        date = driver.find_element_by_xpath(xpath + "/dl/dd/h4/span").text
        content = driver.find_element_by_xpath(xpath + "/dl/dd/ol").text

        if insert_event_list(conn, cur, company, date, image, title, content):
            message = title + ' inserted in db' + '\n'
            print(message)

    driver.close()


def get_bbq_event(conn, cur):
    company = "bbq"
    driver = Chrome()
    driver.get(URL_4)

    driver.implicitly_wait(100)
    xpath = "//*[@class=\"wrapper\"]/div[2]/article/div[2]/div[1]/div[1]/a/img"
    event = driver.find_element_by_xpath(xpath)

    image = event.get_attribute("src")
    event.click()
    time.sleep(2)

    title_loc = driver.find_element_by_xpath("//*[@class=\"wrapper\"]/div[2]/article/div[2]/div[1]/h3")
    title = title_loc.text
    print(title)

    date_loc = driver.find_element_by_xpath("//*[@class=\"wrapper\"]/div[2]/article/div[2]/div[1]/ul/li[1]")
    date = date_loc.text
    print(date)

    content_loc = driver.find_element_by_xpath("//*[@class=\"wrapper\"]/div[2]/article/div[2]/div[2]/img")
    content = content_loc.get_attribute("src")
    print(content)
    print(image)

    driver.back()

    if insert_event_list(conn, cur, company, date, image, title, content):
        message = title + ' inserted in db' + '\n'
        print(message)

    time.sleep(2)

    driver.implicitly_wait(100)
    xpath = "//*[@class=\"wrapper\"]/div[2]/article/div[2]/div[2]/div[1]/a/img"
    event = driver.find_element_by_xpath(xpath)

    image = event.get_attribute("src")
    event.click()
    time.sleep(2)

    title_loc = driver.find_element_by_xpath("//*[@class=\"wrapper\"]/div[2]/article/div[2]/div[1]/h3")
    title = title_loc.text
    print(title)

    date_loc = driver.find_element_by_xpath("//*[@class=\"wrapper\"]/div[2]/article/div[2]/div[1]/ul/li[1]")
    date = date_loc.text
    print(date)

    content_loc = driver.find_element_by_xpath("//*[@class=\"wrapper\"]/div[2]/article/div[2]/div[2]/p/img")
    content = content_loc.get_attribute("src")
    print(content)
    print(image)

    driver.back()

    if insert_event_list(conn, cur, company, date, image, title, content):
        message = title + ' inserted in db' + '\n'
        print(message)

    time.sleep(2)

    driver.implicitly_wait(100)
    xpath = "//*[@class=\"wrapper\"]/div[2]/article/div[2]/div[3]/div[1]/a/img"
    event = driver.find_element_by_xpath(xpath)

    image = event.get_attribute("src")
    event.click()
    time.sleep(2)

    title_loc = driver.find_element_by_xpath("//*[@class=\"wrapper\"]/div[2]/article/div[2]/div[1]/h3")
    title = title_loc.text
    print(title)

    date_loc = driver.find_element_by_xpath("//*[@class=\"wrapper\"]/div[2]/article/div[2]/div[1]/ul/li[1]")
    date = date_loc.text
    print(date)

    content_loc = driver.find_element_by_xpath("//*[@class=\"wrapper\"]/div[2]/article/div[2]/div[2]/p/a/img")
    content = content_loc.get_attribute("src")
    print(content)
    print(image)

    driver.back()

    if insert_event_list(conn, cur, company, date, image, title, content):
        message = title + ' inserted in db' + '\n'
        print(message)

    time.sleep(2)
    driver.implicitly_wait(100)
    xpath = "//*[@class=\"wrapper\"]/div[2]/article/div[2]/div[4]/div[1]/a/img"
    event = driver.find_element_by_xpath(xpath)

    image = event.get_attribute("src")
    event.click()
    time.sleep(2)

    title_loc = driver.find_element_by_xpath("//*[@class=\"wrapper\"]/div[2]/article/div[2]/div[1]/h3")
    title = title_loc.text
    print(title)

    date_loc = driver.find_element_by_xpath("//*[@class=\"wrapper\"]/div[2]/article/div[2]/div[1]/ul/li[1]")
    date = date_loc.text
    print(date)

    content_loc = driver.find_element_by_xpath("//*[@class=\"wrapper\"]/div[2]/article/div[2]/div[2]/p/img")
    content = content_loc.get_attribute("src")
    print(content)
    print(image)

    driver.back()

    if insert_event_list(conn, cur, company, date, image, title, content):
        message = title + ' inserted in db' + '\n'
        print(message)

    driver.close()


def get_pc_event(conn, cur):
    company = "pascucci"
    driver = Chrome()
    driver.get(URL_5)

    driver.implicitly_wait(100)
    xpath_front = "//*[@id=\"container\"]/div[3]/div/ul/li["
    xpath_rear = "]/figure"

    time.sleep(3)
    popup = driver.find_element_by_xpath("//*[@id=\"ch-plugin-core\"]/div[4]/div/div[1]/div")
    popup.click()

    for i in range(1, 11):
        time.sleep(2)
        xpath = xpath_front + str(i) + xpath_rear

        image_loc = driver.find_element_by_xpath(xpath + "/img")
        image = image_loc.get_attribute("src")

        title_loc = driver.find_element_by_xpath(xpath + "/figcaption/h1")
        title = title_loc.text

        content_loc = driver.find_element_by_xpath(xpath + "/figcaption/p")
        content = content_loc.text

        date_loc = driver.find_element_by_xpath(xpath + "/figcaption/span")
        date = date_loc.text

        if insert_event_list(conn, cur, company, date, image, title, content):
            message = title + ' inserted in db' + '\n'
            print(message)

    driver.close()


def get_edy_event(conn, cur):
    company = "ediya"
    driver = Chrome()
    driver.get(URL_6)

    driver.implicitly_wait(100)
    xpath_front = "//*[@id=\"contentWrap\"]/div[2]/div[2]/div/ul/li["
    xpath_rear = "]"

    for i in range (1, 11):
        time.sleep(2)
        xpath = xpath_front + str(i) + xpath_rear

        image_loc = driver.find_element_by_xpath(xpath + "/div[1]/a/img")
        image = image_loc.get_attribute("src")

        title_loc = driver.find_element_by_xpath(xpath + "/dl/dt/a")
        title = title_loc.text

        date_loc = driver.find_element_by_xpath(xpath + "/dl/dd")
        date = date_loc.text
        date = date.split(":")[1]

        image_loc.click()
        time.sleep(2)

        content_loc = driver.find_element_by_xpath("//*[@id=\"contentWrap\"]/div[2]/div[2]/div/form/div[3]/p[1]/img")
        content = content_loc.get_attribute("src")

        if insert_event_list(conn, cur, company, date, image, title, content):
            message = title + ' inserted in db' + '\n'
            print(message)

        driver.back()

    driver.close()


def get_ph_event(conn, cur):
    company = "pizza hut"
    driver = Chrome()
    driver.get(URL_7)

    driver.implicitly_wait(100)
    event_loc = driver.find_element_by_xpath("//*[@id=\"gnb\"]/ul/li[3]/a")
    event_loc.click()

    driver.implicitly_wait(100)
    xpath_front = "//*[@id=\"event\"]/div/div/div[3]/ul/li["
    xpath_rear = "]"

    for i in range(1, 9):
        time.sleep(2)
        xpath = xpath_front + str(i) + xpath_rear

        image_loc = driver.find_element_by_xpath(xpath + "/a")
        image = image_loc.get_attribute("style")
        image = image.split("(")[1]
        image = image.split(")")[0]
        image = image.replace("\"", "")

        image_loc.click()
        time.sleep(3)

        title_loc = driver.find_element_by_xpath("//*[@id=\"event\"]/div/div/div[3]/div[1]")
        title = title_loc.text

        date_loc = driver.find_element_by_xpath("//*[@id=\"event\"]/div/div/div[3]/div[2]")
        date = date_loc.text

        content_loc = driver.find_element_by_xpath("//*[@id=\"event\"]/div/div/div[4]/div/div/span/img")
        content = content_loc.get_attribute("src")

        if insert_event_list(conn, cur, company, date, image, title, content):
            message = title + ' inserted in db' + '\n'
            print(message)

        driver.back()

    driver.close()


if __name__ == "__main__":
    #initialize db
    conn, cur = connect_sqlite3("event.db")

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    while True:
        get_ph_event(conn, cur)

        time.sleep(1800)

