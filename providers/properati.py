from bs4 import BeautifulSoup
import logging
from providers.base_provider import BaseProvider

class Properati(BaseProvider):
    def props_in_source(self, source):
        page_link = self.provider_data['base_url'] + source
        page = 1

        while True:
            logging.info("Requesting %s" % page_link)
            page_response = self.request(page_link)

            if page_response.status_code != 200:
                break

            page_content = BeautifulSoup(page_response.content, 'lxml')
            properties = page_content.find_all('div', class_='listing-card')

            if len(properties) == 0:
                break

            for prop in properties:
                title = prop.find('div', class_='listing-card__title').get_text().strip()
                price = prop.find('div', class_='price').get_text().strip()
                if price is not None:
                    title = title + ' ' + price
                href = self.provider_data['base_url'] + prop['data-href']
                internal_id = prop['data-href'].split('/')[2]

                yield {
                    'title': title,
                    'url': href,
                    'internal_id': internal_id,
                    'provider': self.provider_name,
                    'price': None,
                    'expenses': None,
                    'neighborhood': None,
                    'm2': None,
                    'ambs': None
                }

            page += 1
            page_link = self.provider_data['base_url'] + source + "/%s/" % page
