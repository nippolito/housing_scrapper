from bs4 import BeautifulSoup
import logging
from providers.base_provider import BaseProvider


class Zonaprop(BaseProvider):
    def props_in_source(self, source):
        page_link = self.provider_data['base_url'] + source
        page = 1
        processed_ids = []

        while(True):
            logging.info(f"Requesting {page_link}")
            page_response = self.request(page_link)
            
            if page_response.status_code != 200:
                break
            
            page_content = BeautifulSoup(page_response.content, 'lxml')
            properties = page_content.find_all('div', {'data-qa': 'posting PROPERTY'})

            for prop in properties:
                # if data-id was already processed we exit
                if prop['data-id'] in processed_ids:
                    return
                processed_ids.append(prop['data-id'])
                logging.info(prop['data-id'])
                title = prop.find('a').get_text().strip()
                price = prop.find('div', {'data-qa': 'POSTING_CARD_PRICE'}).get_text().strip()
                expenses = prop.find('div', class_='gIHCpf').find('div', {'data-qa': 'expensas'})
                if expenses:
                    expenses = expenses.get_text().strip()
                neighborhood = prop.find('div', {'data-qa': 'POSTING_CARD_LOCATION'}).get_text().strip()
                features = prop.find('div', {'data-qa': 'POSTING_CARD_FEATURES'}).find_all('span', recursive=False)

                processed_features = []
                for span in features:
                    processed_features.append(span.find('span').get_text().strip())

                # all_m2 = processed_features[0]
                m2 = processed_features[1]
                ambs = processed_features[2]
                # dorms = processed_features[3]
                # bathrooms = processed_features[4]

                yield {
                    'title': title, 
                    'url': self.provider_data['base_url'] + prop['data-to-posting'],
                    'internal_id': prop['data-id'],
                    'provider': self.provider_name,
                    'price': price,
                    'expenses': expenses,
                    'neighborhood': neighborhood,
                    'm2': m2,
                    'ambs': ambs
                }

            page += 1
            page_link = self.provider_data['base_url'] + source.replace(".html", f"-pagina-{page}.html")
