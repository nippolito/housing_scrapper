from bs4 import BeautifulSoup
import logging
import re
from providers.base_provider import BaseProvider

class Mercadolibre(BaseProvider):
    def props_in_source(self, source):
        page_link = self.provider_data['base_url'] + source + '_NoIndex_True'
        from_ = 1
        regex = r"(MLA-\d*)"

        while(True):
            logging.info(f"Requesting {page_link}")
            page_response = self.request(page_link)

            if page_response.status_code != 200:
                break

            page_content = BeautifulSoup(page_response.content, 'lxml')
            properties = page_content.find_all('div', class_='ui-search-result__wrapper')

            if len(properties) == 0:
                break

            for prop in properties:
                section = prop.find('a', class_='ui-search-result__content-link')
                href = section['href']
                matches = re.search(regex, href)
                internal_id = matches.group(1).replace('-', '')
                symbol = section.find('span', class_='price-tag-symbol').get_text().strip()
                price = section.find('span', class_='price-tag-fraction').get_text().strip()
                title = section.select('h2.ui-search-item__title')[0].get_text().strip()
                ambs = section.find('div', class_='ui-search-result__content-attributes').get_text().strip()
                neighborhood = section.find('div', class_='ui-search-result__content-location').get_text().strip()
        
                yield {
                    'title': title, 
                    'url': href,
                    'internal_id': internal_id,
                    'provider': self.provider_name,
                    'price': symbol + price,
                    'expenses': None,
                    'neighborhood': neighborhood,
                    'm2': None,
                    'ambs': ambs
                }

            from_ += 50
            page_link = self.provider_data['base_url'] + source + f"_Desde_{from_}_NoIndex_True"
