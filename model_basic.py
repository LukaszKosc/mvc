
import backend_basic
import mvc_exceptions as mvc_exc

class ModelBasic:
    def __init__(self, app_items):
        self._item_type = 'product'
        self.create_items(app_items)

    @property
    def item_type(self):
        return self._item_type

    @item_type.setter
    def item_type(self, new_item_type):
        self._item_type = new_item_type

    def create_item(self, name, price, quantity):
        backend_basic.create_item(name, price, quantity)

    def create_items(self, items):
        backend_basic.create_items(items)

    def read_item(self, name):
        return backend_basic.read_item(name)

    def read_items(self):
        return backend_basic.read_items()

    def update_item(self, name, price, quantity):
        backend_basic.update_item(name, price, quantity)

    def delete_item(self, name):
        backend_basic.delete_item(name)

    def disconnect(self):
        global items
        if 'items' in globals():
            del items

    def __del__(self):
        self.disconnect()