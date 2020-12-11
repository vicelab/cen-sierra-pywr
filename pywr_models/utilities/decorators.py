from functools import wraps


def catch(f):
    @wraps
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except:
            print('failed!!')

    return wrapper
