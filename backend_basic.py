import mvc_exceptions as mvc_exc

# backend_basic.py
items = list()  # global variable where we keep the data


def create_items(app_items):
    global items
    items = app_items


def create_item(name, price, quantity):
    global items
    results = list(filter(lambda x: x['name'] == name, items))
    if results:
        raise mvc_exc.ItemAlreadyStored(f'Item with name: "{name}"')
    else:
        items.append({'name': name, 'price': price, 'quantity': quantity})


def read_item(name):
    global items
    myitems = list(filter(lambda x: x['name'] == name, items))
    if myitems:
        return myitems[0]
    else:
        raise mvc_exc.ItemNotStored(f'Item with name: "{name}"')


def read_items():
    global items
    return [item for item in items]


# def read_items_filtered(above, feature):
#     global items
#     if above == True:
#         items =list(filter(lambda x: x[feature] > 4, items))
#     return [item for item in items]

def update_item(name, price, quantity):
    global items
    # Python 3.x removed tuple parameters unpacking (PEP 3113), so we have to do it manually (i_x is a tuple, idxs_items is a list of tuples)
    found_item = list(filter(lambda x: x[1]['name'] == name, enumerate(items)))
    if found_item:
        item = items[found_item[0][0]]
        item['price'] = price
        item['quantity'] = quantity
    else:
        raise mvc_exc.ItemNotStored(f'name: "{name}" not stored')


def delete_item(name):
    global items
    # Python 3.x removed tuple parameters unpacking (PEP 3113), so we have to do it manually (i_x is a tuple, idxs_items is a list of tuples)
    found_item = list(filter(lambda x: x[1]['name'] == name, enumerate(items)))
    if found_item:
        del items[found_item[0][0]]
    else:
        raise mvc_exc.ItemNotStored(f'name: "{name}" not stored')
