import pprint


def inspect(data, query_items, show_keys_only=False):
    while len(query_items):
        try:
            key = query_items[0]
            try:
                data = data[int(key)]
            except:
                data = data[key]
            query_items.remove(key)
        except KeyError as e:
            print(data.keys())
            raise e
    if show_keys_only:
        pprint.pprint(data.keys())
    else:
        pprint.pprint(data)
