from functools import reduce as __reduce

def find(check, items):
    return next((item for item in items if check(item)), None)

def filter_list(check, items):
    return list(filter(check, items))

def reduce(check, giveback, items):
    return __reduce(lambda a, b: giveback(a, b) if check(a) else b, items)

def map_list(work, items):
    return list(map(work, items))