import logging
import sqlite3
from providers.zonaprop import Zonaprop
from providers.argenprop import Argenprop
from providers.mercadolibre import Mercadolibre
from providers.properati import Properati
from providers.inmobusqueda import Inmobusqueda


def register_property(conn, prop):
    stmt = 'INSERT INTO properties (internal_id, provider, url) VALUES (:internal_id, :provider, :url)'
    try:
        conn.execute(stmt, prop)
    except Exception as e:
        print(e)


def process_properties(provider_name, provider_data, filters=None):
    provider = get_instance(provider_name, provider_data, filters)

    new_properties = []

    # db connection
    conn = sqlite3.connect('properties.db')

    # Check to see if we know it
    stmt = 'SELECT * FROM properties WHERE internal_id=:internal_id AND provider=:provider'

    with conn:
        for prop in provider.next_prop():
            cur = conn.cursor()
            logging.info(f"Processing id: {prop['internal_id']}")
            cur.execute(stmt, {'internal_id': prop['internal_id'], 'provider': prop['provider']})
            result = cur.fetchone()
            cur.close()
            if not result:
                # Insert and save for notification
                logging.info('It is a new one')
                is_out = provider.filter_unwanted(prop)
                logging.info(is_out)
                if is_out:
                    continue
                register_property(conn, prop)
                new_properties.append(prop)
                    
    return new_properties


def get_instance(provider_name, provider_data, filters):
    if provider_name == 'zonaprop':
        return Zonaprop(provider_name, provider_data, filters)
    elif provider_name == 'argenprop':
        return Argenprop(provider_name, provider_data, filters)
    elif provider_name == 'mercadolibre':
        return Mercadolibre(provider_name, provider_data, filters)
    elif provider_name == 'properati':
        return Properati(provider_name, provider_data, filters)
    elif provider_name == 'inmobusqueda':
        return Inmobusqueda(provider_name, provider_data, filters)
    else:
        raise Exception('Unrecognized provider')
