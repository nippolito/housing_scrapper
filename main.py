#!/usr/bin/env python

import logging
import sqlite3
import time
import yaml

from lib.notifier import Notifier
from providers.processor import process_properties

SLEEP_SECONDS = 30

# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# notify from db
conn = sqlite3.connect('properties.db')
conn.row_factory = dict_factory
stmt = """SELECT title, url, internal_id, provider, price, expenses, neighborhood, m2, ambs
          FROM properties WHERE notified = FALSE"""


# configuration    
with open("configuration.yml", 'r') as ymlfile:
    cfg = yaml.safe_load(ymlfile)

disable_ssl = False
if 'disable_ssl' in cfg:
    disable_ssl = cfg['disable_ssl']

notifier = Notifier.get_instance(cfg['notifier'], disable_ssl, highlighters=cfg['highlighters'])


while True:

    for provider_name, provider_data in cfg['providers'].items():
        try:
            logging.info(f"Processing provider {provider_name}")
            process_properties(provider_name, provider_data, filters=cfg['filters'])
        except Exception as e:
            logging.info(e)
            logging.error(f"Error processing provider {provider_name}.\n{str(e)}")

    new_properties = []

    with conn:
        cur = conn.cursor()
        cur.execute(stmt)
        result = cur.fetchall()
        cur.close()
        if result:
            for prop in result:
                new_properties.append(prop)

    if len(new_properties) > 0:
        logging.info("New properties appeared!")
        # notifier.notify(new_properties)

    logging.info(f"Sleeping..., will continue in {SLEEP_SECONDS} seconds")
    time.sleep(SLEEP_SECONDS)
