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
            properties = page_content.find_all('li', class_='ui-search-layout__item')

            if len(properties) == 0:
                break

            for prop in properties:
                section = prop.find('a', class_='ui-search-result__link')
                if section is None:
                    section = prop.find('a', class_='ui-search-result__content')
                href = section['href']
                matches = re.search(regex, href)
                internal_id = matches.group(1).replace('-', '')
                symbol = section.find('span', class_='price-tag-symbol').get_text().strip()
                price = section.find('span', class_='price-tag-fraction').get_text().strip()
                title = section.select('h2.ui-search-item__title.ui-search-item__group__element.shops__items-group-details.shops__item-title')[0].get_text().strip()

                feature = section.find('ul', class_='shops__items-group-details').find_all('li', class_='ui-search-card-attributes__attribute')
                try:
                    m2 = feature[0].get_text().strip()
                    ambs = feature[1].get_text().strip()
                except Exception as e:
                    logging.info(prop)
                    logging.info(section)
                    logging.info(feature)
                    raise e
                neighborhood = section.select('span.ui-search-item__group__element.ui-search-item__location.shops__items-group-details')[0].get_text().strip()
        
                yield {
                    'title': title, 
                    'url': href,
                    'internal_id': internal_id,
                    'provider': self.provider_name,
                    'price': symbol + price,
                    'expenses': None,
                    'neighborhood': neighborhood,
                    'm2': m2,
                    'ambs': ambs
                }

            from_ += 50
            page_link = self.provider_data['base_url'] + source + f"_Desde_{from_}_NoIndex_True"
    
