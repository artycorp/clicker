#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import datetime
import traceback

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

DATE_FORMAT = "%Y-%m-%d %H:%M"

class NeedRestartTor(Exception):
    pass

class Search:
    logger = None
    browser = None
    profile = None
    query = None
    CITY = u'Perm'
    cntElems = 0 # количество элементов для поиска на странице
    MAX_SERACHED_ITEMS = 5
    YANDEX_XPATH = u"//a[@href='{0}']"
    needRestart = True
    file = None


    def __init__(self, query, logger,max_items):
        self.logger = logger
        self.query = query
        self.browser = None
        self.MAX_SERACHED_ITEMS = max_items
        self.file = open("query.txt", "a")

    def __enter__(self):
        return self

    def destroy(self):
        try:
            self.file.close()
            if not (self.browser is None):
                self.browser.stop_client()
                self.browser.quit()
        except Exception as err:
            traceback.print_exc()
        self.browser = None

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.info("__exit__")
        self.destroy()

    def clean(self):
        """Reset values to default"""
        self.cntElems = 0

    def restart(self):
        return self.needRestart

    def restartTor(self):
        self.clean()
        self.logger.debug("success restart tor")

    def initPreference(self):
        """settings for TOR connect"""
        self.profile = webdriver.FirefoxProfile()
        self.logger.debug("success init preference")

    def check_errors(self):
        str = self.browser.page_source
        res = str.find(u'нашему сервису временно запрещён!')
        if res != -1:
            return True
        res = str.find(u'<title>Ой!</title>')
        if res != -1:
            return True
        res = str.find(u'Введите, пожалуйста, символы с картинки в поле ввода')
        if res != -1:
            return True
        return False


    def initYandex(self):
        """setup yandex to start search"""
        self.browser = webdriver.Firefox(self.profile)

        self.browser.maximize_window()
        self.browser.get('https://www.yandex.ru/')
        if self.check_errors():
            raise NeedRestartTor("initYandex")

    # search query string in yandex
    def findQueryYA(self):
        input = self.browser.find_element_by_xpath("// input[ @ id = 'text']")
        ActionChains(self.browser) \
            .send_keys(Keys.HOME) \
            .perform()
        for ch in self.query:
            ActionChains(self.browser) \
                .send_keys(ch) \
                .perform()
                #.send_keys(Keys.HOME) \
            #.send_keys(self.query) \
            #.send_keys(Keys.END) \
            #.send_keys(Keys.ENTER)\
            #.perform()
            self.browser.implicitly_wait(1)
        ActionChains(self.browser) \
            .move_to_element(input) \
            .send_keys(Keys.ENTER)\
            .perform()


    def getCntElems(self, query):
        elems = self.browser.find_elements_by_xpath(query)
        i = 1
        for elem in elems:
            if i > self.MAX_SERACHED_ITEMS:
                break

            time = datetime.datetime.now().strftime(DATE_FORMAT)
            self.file.write(u'{}-{}-{}\n'.format(time, str(i), elem.text).encode('utf8'))
            i += 1


    def Search(self):
        self.findQueryYA()
        self.browser.implicitly_wait(2)

        if self.check_errors():
            raise NeedRestartTor("Search")

        try:
            self.file.write(self.query.encode("UTF-8") + "\n")
            self.getCntElems("//li[@data-cid]/div/div[2]/div[1]/a")
        except:
            self.logger.error("error in getCntElems")

        if self.check_errors():
            raise NeedRestartTor("Search")

        self.needRestart = False