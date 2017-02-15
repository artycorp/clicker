#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import datetime
import traceback

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from stem import Signal
from stem.control import Controller

DATE_FORMAT = "%d/%m/%Y %H:%M:%S"

class NeedRestartTor(Exception):
    pass

class Search:
    logger = None
    ui_log = None
    browser = None
    profile = None
    query = None
    CITY = u'Perm'
    link = None
    iPage = 1 # page number on search
    cntElems = 0 # количество элементов для поиска на странице
    MAX_SERACHED_ITEMS = 5
    YANDEX_XPATH = u"//a[@href='{0}']"
    needRestart = True


    def __init__(self, query, logger,max_items):
        self.logger = logger
        self.query = query
        self.browser = None
        self.MAX_SERACHED_ITEMS = max_items
        self.ui_log = open(os.getenv('COUNTER_SETTINGS_PATH','') + "ui.log", "a")

    def __enter__(self):
        return self

    def destroy(self):
        try:
            if not (self.browser is None):
                self.browser.stop_client()
                self.browser.quit()
        except Exception as err:
            traceback.print_exc()
        if not self.ui_log is None:
            self.ui_log.close()
            self.ui_log = None
        self.browser = None

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.info("__exit__")
        self.destroy()

    def writeUiLog(self, searcher, qry):
        d = datetime.datetime.now()
        self.ui_log.write("{0} | ".format(d.strftime(DATE_FORMAT)))
        self.ui_log.write("{0} | ".format(searcher.encode("utf8")))
        self.ui_log.write("{0} | ".format(qry.encode("utf8")))

    def clean(self):
        """Reset values to default"""
        self.iPage = 1
        self.cntElems = 0

    def restart(self):
        self.ui_log = open(os.getenv('COUNTER_SETTINGS_PATH', '') + "ui.log", "a")
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

    def submitRegion(self):
        """push submit region button"""
        btn = self.browser.find_element_by_xpath("//button[@type='submit']")

        try:
            ActionChains(self.browser) \
                .move_to_element(btn) \
                .send_keys_to_element(btn, Keys.ENTER) \
                .perform()
        except:
            self.logger.error("Submit Region error")
            return True # need restart set region
        return False

    # search query string in yandex
    def findQueryYA(self):
        input = self.browser.find_element_by_xpath("// input[ @ id = 'text']")
        for ch in self.query:
            ActionChains(self.browser) \
                .move_to_element(input) \
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
        i = 0
        for elem in elems:
            if i > self.MAX_SERACHED_ITEMS:
                break
            # пропустить первый элемент говнокод:(
            if i > 0:
                print(elem.get_attribute("href"))
            i = i + 1


    def Search(self):
        self.findQueryYA()
        self.browser.implicitly_wait(2)

        if self.check_errors():
            raise NeedRestartTor("Search")

        try:
            self.getCntElems("//li[@data-cid]/div/div[1]/div[1]/a[1][@href]")
        except:
            self.logger.error("error in getCntElems")

        if self.check_errors():
            raise NeedRestartTor("Search")

        self.needRestart = False
        self.writeUiLog(searcher="Not found Yandex", qry=self.query)