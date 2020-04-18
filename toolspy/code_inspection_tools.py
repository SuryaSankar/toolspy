from functools import wraps
from datetime import datetime


def scd(cls):
    if len(cls.__subclasses__())==0:
        return {}
    return {x: scd(x) for x in cls.__subclasses__()}

def all_subclasses(cls):
    return cls.__subclasses__() + [
        g for s in cls.__subclasses__() for g in all_subclasses(s)]

def correct_subclass(klass, discriminator):
    try:
        return next(
            c for c in all_subclasses(klass)
            if c.__mapper_args__['polymorphic_identity'] == discriminator)
    except:
        return None


def with_execution_timedelta(f):

    @wraps(f)
    def wrapped_func(*args, **kwargs):
        start_time = datetime.utcnow()
        result = f(*args, **kwargs)
        elapsed_timedelta = datetime.utcnow() - start_time
        return (result, elapsed_timedelta)
    return wrapped_func