import logging
import sqlite3
from providers.zonaprop import Zonaprop
from providers.argenprop import Argenprop
from providers.mercadolibre import Mercadolibre
from providers.properati import Properati
from providers.inmobusqueda import Inmobusqueda


def register_property(conn, prop):
    stmt = """INSERT INTO properties (
                title
                , url
                , internal_id
                , provider
                , price
                , expenses
                , neighborhood
                , m2
                , ambs
        ) VALUES (
                :title
                , :url
                , :internal_id
                , :provider
                , :price
                , :expenses
                , :neighborhood
                , :m2
                , :ambs
        )"""
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
    get_property_statement = 'SELECT * FROM properties WHERE internal_id=:internal_id AND provider=:provider'

    with conn:
        for prop in provider.next_prop():
            cur = conn.cursor()
            logging.info(f"Processing id: {prop['internal_id']}")
            cur.execute(get_property_statement, {
                'internal_id': prop['internal_id'],
                'provider': prop['provider']
            })
            result = cur.fetchone()
            cur.close()
            if not result:
                # Insert and save for notification
                logging.info('It is a new one')
                is_out = provider.filter_unwanted(prop)
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
