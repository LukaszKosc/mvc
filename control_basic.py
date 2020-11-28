from model_basic import ModelBasic
from view import View
from controller import Controller

if __name__ == '__main__':
    try:
        my_items = [
            {'name': 'x4', 'price': 1, 'quantity': 4},
            {'name': 'x1', 'price': 2, 'quantity': 4},
            {'name': 'x2', 'price': 3, 'quantity': 4},
            {'name': 'x', 'price': 5, 'quantity': 4},
            {'name': 'x5', 'price': 7, 'quantity': 4}
        ]

        c = Controller(ModelBasic(my_items), View())
        c.show_items()
        c.show_items(bullet_points=True)
        c.show_item('x4')
        c.insert_item('x8', 4, 5)
        name = 'x9'
        try:
            c.insert_item(name, 0, 5)
        except AssertionError as e:
            print(f'Problem occured while adding product {name}:', e)
        c.show_item('x9')
        c.insert_item('bread', 1, 10)
        c.show_item('bread')
        c.show_item('x9')
        c.delete_item('bread')
        c.show_item('bread')
    except Exception as e:
        # print(e)
        pass
