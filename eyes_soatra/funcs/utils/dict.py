def sort_dict(dict):
    keys = list(dict.keys())
    keys.sort()
    new_dict = {}
    
    for key in keys:
        new_dict[key] = dict[key]
    
    return new_dict