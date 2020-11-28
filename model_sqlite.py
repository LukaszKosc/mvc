import backend_sqlite
import mvc_exceptions as mvc_exc


class ModelSQLite(object):

    def __init__(self, application_items):
        self._item_type = 'product'
        self._connection = backend_sqlite.connect_to_db(backend_sqlite.DB_name)
        backend_sqlite.create_table(self.connection, self._item_type)
        self.create_items(application_items)

    @property
    def connection(self):
        return self._connection

    @property
    def item_type(self):
        return self._item_type

    @item_type.setter
    def item_type(self, new_item_type):
        self._item_type = new_item_type

    def create_item(self, name, price, quantity):
        backend_sqlite.insert_one(
            self.connection, name, price, quantity, table_name=self.item_type)

    def create_items(self, items):
        backend_sqlite.insert_many(
            self.connection, items, table_name=self.item_type)

    def read_item(self, name):
        return backend_sqlite.select_one(
            self.connection, name, table_name=self.item_type)

    def read_items(self):
        return backend_sqlite.select_all(
            self.connection, table_name=self.item_type)

    def update_item(self, name, price, quantity):
        backend_sqlite.update_one(
            self.connection, name, price, quantity, table_name=self.item_type)

    def delete_item(self, name):
        backend_sqlite.delete_one(
            self.connection, name, table_name=self.item_type)

    def disconnect(self):
        try:
            if self.connection:
                self.connection.close()
        except backend_sqlite.sqlite3.ProgrammingError as e:
            print(e)

    def __del__(self):
        self.disconnect()
