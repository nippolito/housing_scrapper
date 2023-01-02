import logging
import cloudscraper
from abc import ABC, abstractmethod
from lib.hostname_ignoring_adapter import HostNameIgnoringAdapter
import yaml

# configuration    
with open("configuration.yml", 'r') as ymlfile:
    print('loading config')
    cfg = yaml.safe_load(ymlfile)

disable_ssl = False

if 'disable_ssl' in cfg:
    disable_ssl = cfg['disable_ssl']
class BaseProvider(ABC):
    def __init__(self, provider_name, provider_data, filters):
        self.provider_name = provider_name
        self.provider_data = provider_data
        self.filters = filters
        self.__scraper = cloudscraper.create_scraper()
        if disable_ssl:
            self.__scraper.mount('https://', HostNameIgnoringAdapter())
    
    @abstractmethod
    def props_in_source(self, source):
        pass

    def request(self, url):
        return self.__scraper.get(url, verify=not disable_ssl)

    def next_prop(self):
        for source in self.provider_data['sources']:
            logging.info(f'Processing source {source}')
            yield from self.props_in_source(source)

    def filter_unwanted(self, prop):
        if not self.filters:
            return False
        forbidden_words = self.filters.get('forbidden_words')
        if forbidden_words:
            for key, forbidden_values in forbidden_words.items():
                for word in forbidden_values:
                    if word in prop[key].lower():
                        logging.info(f'Filtered because it contains word: {word}')
                        return True

        return False
