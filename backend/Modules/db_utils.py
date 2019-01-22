import json


def get_array_result(data):

    if not data:
        return None

    if len(data):
        data = data[1]
        if not data:
            return None
        data = json.loads(data)
        return data

    return None


def get_single_result(data):
    print("data: ", data)

    if not data:
        return None

    if len(data):
        data = data[1]
        if not data:
            return None

        data = json.loads(data)
        if len(data):
            data = data[0]
    else:
        data = None
    return data


def load_json_string(data):
    print(data)

    if not data:
        return None

    if data and len(data):
        print("is array")
        for d in data:
            if not d:
                break
            d['json_config'] = json.loads(d["json_config"])
    else:
        data = json.loads(data["json_config"])
    return data

def load_json_string_collection(data1):
    data = {}
    print(data1)

    if not data1:
        return None

    for d in data1:
        data[d["collection"]] = json.loads(d["json_config"])
    return data