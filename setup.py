import sqlite3

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
 
    return None


def execute(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
        c.close()
    except Exception as e:
        print(e)


database = "properties.db"

sql_create_properties_table = """ CREATE TABLE IF NOT EXISTS properties (
                                    id integer PRIMARY KEY,
                                    title text NULL,
                                    internal_id text NOT NULL,
                                    provider text NOT NULL,
                                    url text NOT NULL,
                                    price text NULL,
                                    expenses text NULL,
                                    neighborhood text NULL,
                                    m2 text NULL,
                                    ambs text NULL,
                                    captured_date integer DEFAULT CURRENT_TIMESTAMP,
                                    notified boolean DEFAULT FALSE
                                ); """

sql_create_index_on_properties_table = """ CREATE INDEX properties_internal_provider ON properties (internal_id, provider); """

# create a database connection
conn = create_connection(database)
with conn:
    if conn is not None:
        # create properties table
        execute(conn, sql_create_properties_table)
        # create properties indexes
        execute(conn, sql_create_index_on_properties_table)
    else:
        print("Error! cannot create the database connection.")        

       
