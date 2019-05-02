import datetime
import numpy as np


def convert_datetime64_to_datatime(datetime64):
    return datetime.datetime.utcfromtimestamp(
        (datetime64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
    )
