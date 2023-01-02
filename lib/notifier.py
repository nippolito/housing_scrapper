import telegram
import logging
import random
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
        self.bot.send_message(chat_id=self.config['chat_id'], text=text)

        for prop in properties:
            logging.info(f"Notifying about {prop['url']}")
            self.send_message(prop)

    def test(self, message):
        self.bot.send_message(chat_id=self.config['chat_id'], text=message)

    def send_message(self, prop):
        if self.highlighters:
            highlight = self.highlighted_message(prop)

        message = f"[{prop['title']}]({prop['url']})"
        if highlight:
            message = highlight + message

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
