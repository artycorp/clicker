#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import logging
import json

from search import Search
from search import NeedRestartTor


SETTINGS_FILE = os.getenv('COUNTER_SETTINGS_PATH', '') + "settings.json"
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"

def getLogger():
    logger = logging.getLogger("counter")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', DATE_FORMAT)
    #ch = logging.StreamHandler()
    ch = logging.FileHandler(os.getenv('COUNTER_SETTINGS_PATH','') + "mylog.log")
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def loadSettings():
    json_data = None
    with open(SETTINGS_FILE) as json_file:
        json_data = json.load(json_file)
        # print(json_data)
    return json_data['search_texts']

def main():
    logger = getLogger()
    #search_text=u'стиральные машинки'

    try:
        search_texts = loadSettings()
    except:
        logger.error("Cannot read {0}".format(SETTINGS_FILE))
        exit(1)
    for search_text in search_texts:
        with Search(query=search_text["text"], logger=logger, max_items=5) as ya:
            logger.info(search_text)
            while ya.restart():
                ya.restartTor()
                ya.initPreference()
                try:
                    ya.initYandex()
                    ya.Search()
                except NeedRestartTor as err:
                    ya.browser.close()  # close browser window
                    print(err.message)
            ya.destroy()

if __name__ == "__main__":
    main()
