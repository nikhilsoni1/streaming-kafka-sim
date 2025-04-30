import datetime

def get_utc_now(return_as_string=True):
    _now = datetime.datetime.now(datetime.timezone.utc)
    if return_as_string:
        return _now.strftime('%Y-%m-%d %H:%M:%S')
    return _now
