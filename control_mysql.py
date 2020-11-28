import backend_mysql
from controller import Controller
from model_mysql import ModelMySQL
from view import View


backend_mysql.DB_name = 'mydb'


if __name__ == '__main__':

    my_items = [
        {'name': 'bread', 'price': 0.5, 'quantity': 20},
        {'name': 'milk', 'price': 1.0, 'quantity': 10},
        {'name': 'wine', 'price': 10.0, 'quantity': 5},
    ]

    c = Controller(ModelMySQL(my_items), View())
    c.show_items()
    c.show_items(bullet_points=True)
    c.show_item('chocolate')
    c.show_item('bread')

    c.insert_item('bread', price=1.0, quantity=5)
    c.insert_item('chocolate', price=2.0, quantity=10)
    c.show_item('chocolate')

    c.update_item('milk', price=1.2, quantity=20)
    c.update_item('ice cream', price=3.5, quantity=20)

    c.delete_item('fish')
    c.delete_item('bread')

    c.show_items()

    # # we close the current sqlite database connection explicitly
    # if type(c.model) is ModelMySQL:
    #     backend_mysql.disconnect_from_db(c.model.connection)
    #     # backend understands that it needs to open a new connection
    #     c.show_items()
    #     c.insert_item('bread123', price=1.0, quantity=5)
    #     c.show_items()
    #
    del c