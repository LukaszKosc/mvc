import pdb
from sqlite3 import OperationalError, IntegrityError, ProgrammingError
import mvc_exceptions as mvc_exc
import mysql.connector as mysql_connector
from mysql.connector import Error as mysql_error


DB_name = 'mydb'
DB_user = 'lukasz'
DB_pass = 'Password123!'


def connect_to_db(host=None, database=None, user=None, password=None):
    """Connect to a mysql DB. Create the database if there isn't one yet.

    Parameters
    ----------
    host : str
        host name
    database : str
        database name
    user : str
        database user
    password : str
        database password

    Returns
    -------
    connection : mysql.Connection
        connection object
    """
    try:
        # ALTER TABLE testowa AUTO_INCREMENT = 1
        host = host if host else 'localhost'
        database = database if database else DB_name
        user = user if user else DB_user
        password = password if password else DB_pass

        connection = mysql_connector.connect(host=host, database=database, user=user, password=password, port=3306)
        if connection.is_connected():
            return connection
    except mysql_error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
        connection = None
    finally:
        return connection


# TODO: use this decorator to wrap commit/rollback in a try/except block ?
# see http://www.kylev.com/2009/05/22/python-decorators-and-database-idioms/
def connect(func):
    """Decorator to (re)open a database connection when needed.

    A database connection must be open when we want to perform a database query
    but we are in one of the following situations:
    1) there is no connection
    2) the connection is closed

    Parameters
    ----------
    func : function
        function which performs the database query

    Returns
    -------
    inner func : function
    """
    def inner_func(conn, *args, **kwargs):
        if not conn.is_connected():
            conn = connect_to_db()
        return func(conn, *args, **kwargs)
    return inner_func


def disconnect_from_db(connection):
    if connection:
        if connection.is_connected():
            print('backed mysql disconnecting')
            connection.close()
    else:
        print('Connection is None')


def get_cursor(conn):
    return conn.cursor()

@connect
def create_table(conn, table_name):
    table_name = scrub(table_name)
    sql = 'CREATE TABLE IF NOT EXISTS {} (rowid int PRIMARY KEY AUTO_INCREMENT,' \
          'name varchar(255) UNIQUE, price float, quantity int)'.format(table_name)
    try:
        get_cursor(conn).execute(sql)
    except mysql_error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)


def scrub(input_string):
    """Clean an input string (to prevent SQL injection).

    Parameters
    ----------
    input_string : str

    Returns
    -------
    str
    """
    return ''.join(k for k in input_string if k.isalnum())


@connect
def insert_one(conn, name, price, quantity, table_name):
    items = [{'name': name, 'price': price, 'quantity': quantity}]
    try:
        table_name = scrub(table_name)
        sql = "INSERT INTO {} (rowid, name, price, quantity) VALUES (%s, %s, %s, %s)" \
        .format(table_name)
        entries_to_insert = verify_if_item_present(conn, items, table_name)
        get_cursor(conn).executemany(sql, entries_to_insert)
        conn.commit()
    except mysql_error as err:
        raise mvc_exc.ItemAlreadyStored(
            '{}: "{}" already stored in table "{}"'.format(err, name, table_name))


@connect
def verify_if_item_present(conn, items, table_name):
    entries = list()
    items_present = dict()
    for product in items:
        items_present[product['name']] = \
            False if not select_one(conn, product['name'], table_name, verification=True) \
            else True
    for x in items:
        if x['name'] in items_present:
            if not items_present[x['name']]:
                entries.append((0, x['name'], x['price'], x['quantity']))
            else:
                raise mvc_exc.ItemAlreadyStored('Product "{}" is already stored in table "{}"'
                      .format(x['name'], table_name))
    return entries


@connect
def insert_many(conn, items, table_name):
    table_name = scrub(table_name)
    sql = "INSERT INTO {} (rowid, name, price, quantity) VALUES (%s, %s, %s, %s)" \
        .format(table_name)
    entries_to_insert = verify_if_item_present(conn, items, table_name)
    try:
        get_cursor(conn).executemany(sql, entries_to_insert)
        conn.commit()
    except mysql_error as err:
        print('{}: at least one in {} was already stored in table "{}"'
              .format(err, [x['name'] for x in items], table_name))


def tuple_to_dict(mytuple):
    mydict = dict()
    mydict['id'] = mytuple[0]
    mydict['name'] = mytuple[1]
    mydict['price'] = mytuple[2]
    mydict['quantity'] = mytuple[3]
    return mydict


@connect
def select_one(conn, item_name, table_name, verification=False):
    table_name = scrub(table_name)
    item_name = scrub(item_name)
    sql = 'SELECT * FROM {} WHERE name="{}"'.format(table_name, item_name)
    cursor = get_cursor(conn)
    cursor.execute(sql)
    result = cursor.fetchone()
    if result:
        return tuple_to_dict(result)
    else:
        if not verification:
            raise mvc_exc.ItemNotStored(
                'Can\'t read "{}" because it\'s not stored in table "{}"'
                .format(item_name, table_name))
        return None


@connect
def select_all(conn, table_name):
    table_name = scrub(table_name)
    sql = 'SELECT * FROM {}'.format(table_name)
    cursor = get_cursor(conn)
    cursor.execute(sql)
    results = cursor.fetchall()
    return list(map(lambda x: tuple_to_dict(x), results))


@connect
def update_one(conn, name, price, quantity, table_name):
    table_name = scrub(table_name)
    sql_check = 'SELECT EXISTS(SELECT 1 FROM {} WHERE name=%s LIMIT 1)' \
        .format(table_name)
    sql_update = 'UPDATE {} SET price=%s, quantity=%s WHERE name=%s' \
        .format(table_name)
    cursor = get_cursor(conn)
    cursor.execute(sql_check, (name,))  # we need the comma
    result = cursor.fetchone()
    if result[0]:
        cursor.execute(sql_update, (price, quantity, name))
        conn.commit()
    else:
        raise mvc_exc.ItemNotStored(
            'Can\'t update "{}" because it\'s not stored in table "{}"'
                .format(name, table_name))


@connect
def delete_one(conn, name, table_name):
    table_name = scrub(table_name)
    sql_check = 'SELECT EXISTS(SELECT 1 FROM {} WHERE name=%s LIMIT 1)' \
        .format(table_name)
    table_name = scrub(table_name)
    sql_delete = 'DELETE FROM {} WHERE name=%s'.format(table_name)
    try:
        cursor = get_cursor(conn)
        cursor.execute(sql_check, (name,))  # we need the comma
        result = cursor.fetchone()
        conn.commit()

        if result[0]:
            cursor.execute(sql_delete, (name,))  # we need the comma
            conn.commit()
        else:
            raise mvc_exc.ItemNotStored(
                'Can\'t delete "{}" because it\'s not stored in table "{}"'
                    .format(name, table_name))
    except mysql_error as err:
        raise Exception('Unspecified error: {}'.format(err))


@connect
def clean_table(conn, table_name):
    table_name = scrub(table_name)
    cursor = get_cursor(conn)
    delete_sql = f'DELETE FROM {table_name} WHERE rowid>0'

    cursor.execute(delete_sql)
    reset_auto = f'ALTER TABLE {table_name} AUTO_INCREMENT = 1'
    cursor.execute(reset_auto)
    conn.commit()


def main():

    table_name = 'testowa'
    # conn = connect_to_db('myDB')  # in-memory database
    conn = connect_to_db()  # physical database

    create_table(conn, table_name)

    my_items = [
        {'name': 'beer', 'price': 0.5, 'quantity': 1},
        {'name': 'bread', 'price': 0.5, 'quantity': 20},
        {'name': 'milk', 'price': 1.0, 'quantity': 10},
        {'name': 'wine', 'price': 10.0, 'quantity': 5}
    ]


    # CREATE
    table_n = 'testowa'
    clean_table(conn, table_name=table_n)
    # insert_one(conn, 'beer', price=2.0, quantity=5, table_name=table_n)
    insert_many(conn, my_items, table_name=table_n)
    # print(select_one(conn, 'soup', table_name=table_n))
    insert_one(conn, 'soup', price=2.5, quantity=11, table_name=table_n)
    # print('-----------select_one ------------------------')
    # print(select_one(conn, 'soup', table_name=table_n))
    # print('-----------select_one ------------------------')
    # print('-----------select_all ------------------------')
    # print(select_all(conn, table_name=table_n))
    # print('-----------select_all ------------------------')
    # insert_one(conn, 'soup', price=2.5, quantity=11, table_name=table_n)
    # insert_one(conn, 'mix', price=2.5, quantity=11, table_name=table_n)
    print(select_all(conn, table_name=table_n))
    # delete_one(conn, 'soup', table_name=table_n)
    update_one(conn, 'soup', price='11111.00', quantity=234, table_name=table_n)
    print(select_all(conn, table_name=table_n))
    # insert_one(conn, 'soup', price=2.5, quantity=11, table_name=table_n)
    delete_one(conn, 'soup', table_name=table_n)
    print(select_all(conn, table_name=table_n))
    # insert_one(conn, 'beer', price=2.0, quantity=5, table_name='testowa')
    # # if we try to insert an object already stored we get an ItemAlreadyStored
    # # exception
    # # insert_one(conn, 'milk', price=1.0, quantity=3, table_name='items')
    #
    # # READ
    # print('SELECT milk')
    # print(select_one(conn, 'milk', table_name='items'))
    # print('SELECT all')
    # print(select_all(conn, table_name='items'))
    # # if we try to select an object not stored we get an ItemNotStored exception
    # # print(select_one(conn, 'pizza', table_name='items'))
    # select_one(conn, 'beer', 'testowa')
    #
    # # conn.close()  # the decorator  will reopen the connection
    #
    # # UPDATE
    # print('UPDATE bread, SELECT bread')
    # update_one(conn, 'bread', price=1.5, quantity=7, table_name='items')
    # print(select_one(conn, 'bread', table_name='items'))
    # # if we try to update an object not stored we get an ItemNotStored exception
    # # print('UPDATE pizza')
    # # update_one(conn, 'pizza', price=1.5, quantity=5, table_name='items')
    #
    # # DELETE
    # print('DELETE beer, SELECT all')
    # delete_one(conn, 'beer', table_name='items')
    # print(select_all(conn, table_name='items'))
    # # if we try to delete an object not stored we get an ItemNotStored exception
    # # print('DELETE fish')
    # # delete_one(conn, 'fish', table_name='items')
    #
    # # save (commit) the changes
    # # conn.commit()
    #
    # # close connection
    conn.close()


if __name__ == '__main__':
    main()