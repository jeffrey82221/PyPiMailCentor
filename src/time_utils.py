from datetime import datetime


def convert_to_datetime(t):
    try:
        return datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%fZ")
    except:
        return datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")
