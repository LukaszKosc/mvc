import backend_mysql
import mvc_exceptions as mvc_exc


class ModelMySQL(object):

    def __init__(self, application_items):
        self._item_type = 'product'
        self._connection = backend_mysql.connect_to_db()
        backend_mysql.clean_table(self._connection, table_name=self._item_type)
        backend_mysql.create_table(self.connection, self._item_type)
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
        backend_mysql.insert_one(
            self.connection, name, price, quantity, table_name=self.item_type)

    def create_items(self, items):
        backend_mysql.insert_many(
            self.connection, items, table_name=self.item_type)

    def read_item(self, name):
        return backend_mysql.select_one(
            self.connection, name, table_name=self.item_type)

    def read_items(self):
        return backend_mysql.select_all(
            self.connection, table_name=self.item_type)

    def update_item(self, name, price, quantity):
        backend_mysql.update_one(
            self.connection, name, price, quantity, table_name=self.item_type)

    def delete_item(self, name):
        backend_mysql.delete_one(
            self.connection, name, table_name=self.item_type)

    def disconnect(self):
        if self.connection.is_connected():
            self.connection.close()

    def __del__(self):
        self.disconnect()