import datetime
import telegram
import logging
import random
import sqlite3
from lib.sslless_session import SSLlessSession


class NullNotifier:
    def notify(self, properties):
        pass


class Notifier(NullNotifier):
    def __init__(self, config, disable_ssl, highlighters=None):
        logging.info(f"Setting up bot with token {config['token']}")
        self.config = config
        self.highlighters = highlighters
        if disable_ssl:
            self.bot = telegram.Bot(token=self.config['token'], request=SSLlessSession())
        else:
            self.bot = telegram.Bot(token=self.config['token'])

    def notify(self, properties):
        logging.info(f'Notifying about {len(properties)} properties')
        text = random.choice(self.config['messages'])
        self.bot.send_message(chat_id=self.config['chat_id'], text=text.format(today=datetime.date.today()))

        for prop in properties:
            logging.info(f"Notifying about {prop['url']}")
            try:
                self.send_message(prop)
            except telegram.error.TimedOut as e:
                logging.error(e)
                continue

            self.log_notified(prop)

    def test(self, message):
        self.bot.send_message(chat_id=self.config['chat_id'], text=message)

    def log_notified(self, prop):
        conn = sqlite3.connect('properties.db')
        stmt = """UPDATE properties set notified = TRUE WHERE internal_id = :internal_id and provider = :provider"""
        with conn:
            cur = conn.cursor()
            cur.execute(stmt, {
                'internal_id': prop['internal_id'],
                'provider': prop['provider']
            })
            cur.close()

    def send_message(self, prop):
        if self.highlighters:
            highlight = self.highlighted_message(prop)

        message = f"""
        [{prop['title']}]({prop['url']})
        Rooms: {prop['ambs']}
        Price: {prop['price']}
        Expenses: {prop['expenses']}
        m2: {prop['m2']}
        Location: {prop['neighborhood']}"""

        if highlight:
            message = highlight + '\n' + message

        message = message.replace('*', '').replace('_', '')
        self.bot.send_message(chat_id=self.config['chat_id'],
                    text=message,
                    parse_mode=telegram.ParseMode.MARKDOWN)

    def highlighted_message(self, prop):
        indicators = self.highlighters['indicators']
        for key, good_values in indicators.items():
            for word in good_values:
                if word in prop[key].lower():
                    logging.info(f'Property is highlighted because it contains: {word}!')
                    message = self.highlighters['message'].format(word=word)
                    return message

        return None

    @staticmethod
    def get_instance(config, disable_ssl=False, highlighters=None):
        if config['enabled']:
            return Notifier(config, disable_ssl, highlighters=highlighters)
        else:
            return NullNotifier()
