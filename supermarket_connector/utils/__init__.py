from typing import Any, Dict


def process_type(value: Any, temp: Dict[str, Any], get_value: bool = True):
    key = type(value).__name__

    if key in temp.keys():
        temp[key]["counter"] += 1
    else:
        temp[key] = {"counter": 1}

    if key == "dict":
        if "items" in temp[key].keys():
            temp[key]["items"] = type_def_dict(value, temp[key]["items"], get_value)
        else:
            temp[key]["items"] = type_def_dict(value, {}, get_value)

    if key == "list":
        if "len" in temp[key].keys():
            if not len(value) in temp[key]["len"]:
                temp[key]["len"].append(len(value))
                temp[key]["len"] = sorted(temp[key]["len"])
        else:
            temp[key]["len"] = [len(value)]

        for v in value:
            if "items" in temp[key].keys():
                temp[key]["items"] = process_type(v, temp[key]["items"], get_value)
            else:
                temp[key]["items"] = process_type(v, {}, get_value)

    if key != "dict" and key != "list" and get_value:
        if "value" in temp[key].keys():
            temp[key]["value"].append(value)
            temp[key]["value"] = sorted(list(set(temp[key]["value"])))
        else:
            temp[key]["value"] = [value]

    return temp


def type_def_dict(elem: Dict[str, Any], temp: Dict[str, Any], get_value: bool = True):
    for key, value in elem.items():
        if key in temp.keys():
            temp[key] = process_type(value, temp[key], get_value)
        else:
            temp[key] = process_type(value, {}, get_value)

    return temp
