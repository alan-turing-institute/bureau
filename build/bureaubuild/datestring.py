from datetime import datetime

fmt = '%Y%m%dT%H%M%S'


def validate_date_string(date_string):
    try:
        datetime.strptime(date_string, fmt)
    except ValueError:
        return False

    # Ensure zero padding which is optional in strptime
    if len(date_string) != 15:
        return False

    return True


def image_version_string(date_string):
    dt = datetime.strptime(date_string, fmt)
    return dt.strftime('%Y.%m%d.%H%M%S')
