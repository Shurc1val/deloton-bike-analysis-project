"""Module to transform the data received from the Kafka cluster."""

from ast import literal_eval
from datetime import datetime, timedelta


INVALID_DATE_THRESHOLD = datetime(1900, 1, 1, 0, 0, 0)
PREFIXES = ['mr', 'mrs', 'miss', 'ms', 'dr',
            'mr.', 'mrs.', 'miss.', 'ms.', 'dr.']


def timestamp_to_date(timestamp_ms: int | None) -> str | None:
    """Helper function that converts a timestamp in milliseconds
    since the Unix epoch to a date string in the form YYYY-MM-DD."""

    if timestamp_ms is None:
        return timestamp_ms
    return datetime.utcfromtimestamp(timestamp_ms / 1000).date()


def check_datetime_is_valid(dt: datetime) -> bool:
    """Helper function that returns True if a datetime is valid, i.e. each component
    in the datetime is within its appropriate range, or returns False if invalid."""

    if dt > datetime.now() or dt < INVALID_DATE_THRESHOLD:
        return False
    return True


def extract_datetime_from_string(input_string: str) -> datetime | None:
    """Helper function to extract a datetime object from a string that contains
    a datetime in the format 'YYYY-MM-DD HH:MM:SS.microseconds'."""
    datetime_str = " ".join(input_string.split(" ")[:2])
    try:
        if '.' in input_string:
            datetime_format = '%Y-%m-%d %H:%M:%S.%f'
        else:
            datetime_format = '%Y-%m-%d %H:%M:%S'
            
        datetime_obj = datetime.strptime(
            datetime_str, datetime_format)

        if check_datetime_is_valid(datetime_obj):
            return datetime_obj
    except (ValueError, AttributeError):
        return None
    return None


def get_bike_serial_number_from_log_line(log_line: str) -> str | None:
    """Takes in a kafka log line, and returns the bike serial number if found."""

    log_line_dict = literal_eval(log_line.split('=')[1])
    return log_line_dict.get('bike_serial')


def get_email_from_log_line(log_line: str) -> str | None:
    """Helper function to extract an email address from a log line using if found."""

    log_line_dict = literal_eval(log_line.split('=')[1])
    return log_line_dict.get('email_address')


def get_rider_from_log_line(log_line: str) -> dict:
    """Takes in a kafka log line and returns a dictionary of rider data from it (excluding address).
    If any rider information is missing, this field is given as None in the returned dictionary."""

    rider = {}
    log_line_data = literal_eval(log_line.split('=')[1])

    # Obtain rider data from the log line directly
    rider['rider_id'] = int(log_line_data.get('user_id', -1))

    name = log_line_data.get('name')
    if name:
        name_parts = name.split()
        if name_parts[0].lower() in PREFIXES:
            name = ' '.join(name_parts[1:])

        rider['first_name'] = name[:name.rfind(' ')]
        rider['last_name'] = name.split()[-1]
    else:
        rider['first_name'] = None
        rider['last_name'] = None

    rider['birthdate'] = timestamp_to_date(
        log_line_data.get('date_of_birth', None))

    rider['height'] = int(log_line_data.get('height_cm', -1))
    rider['weight'] = int(log_line_data.get('weight_kg', -1))
    rider['email'] = get_email_from_log_line(log_line)

    if log_line_data.get('gender') and \
            log_line_data.get('gender').lower() not in ['male', 'female']:
        rider['gender'] = 'other'
    elif log_line_data.get('gender') and \
            log_line_data.get('gender').lower() in ['male', 'female']:
        rider['gender'] = log_line_data.get('gender')
    else:
        rider['gender'] = None

    rider['account_created'] = timestamp_to_date(
        log_line_data.get('account_create_date', None))

    for key, val in rider.items():
        if val == -1:
            rider[key] = None

    return rider


def get_ride_data_from_log_line(log_line: str) -> dict:
    """
    Takes in a kafka log line and returns a dictionary of ride data from it (corresponding to
    non-auto-generated attributes in ride table in db). If a given field is not found, its value
    in the returned dictionary is given as None.
    """

    ride = {}

    log_line_data = literal_eval(log_line.split('=')[1])

    try:
        ride['rider_id'] = int(log_line_data['user_id'])
    except KeyError:
        ride['rider_id'] = None

    log_datetime = extract_datetime_from_string(log_line)
    if log_datetime:
        ride['start_time'] = log_datetime - timedelta(seconds=0.5)
    else:
        ride['start_time'] = None

    return ride


def get_data_from_reading_line_pair(reading_line_pair: str, start_time: datetime) -> dict:
    """
    Takes in a pair of Kafka reading lines (that have been string concatenated), and extracts and
    transforms reading data from it, returning this as a dictionary.
    """

    reading_lines = reading_line_pair.split('\n')
    reading = {'resistance': None, 'elapsed_time': None, 'heart_rate': None,
               'power': None, 'rpm': None}

    # '[INFO]: Ride' line
    try:
        reading['resistance'] = int(
            reading_lines[0].split(';')[-1].split('=')[1].strip())
    except IndexError:
        reading['resistance'] = None

    log_datetime = extract_datetime_from_string(reading_lines[0])
    if log_datetime and log_datetime > start_time:
        reading['elapsed_time'] = int((log_datetime - start_time).total_seconds())
    else:
        reading['elapsed_time'] = None

    if len(reading_lines) == 1:
        return reading

    # '[INFO]: Telemetry' line
    str_attributes = reading_lines[1].split(';')
    reading['heart_rate'] = int(
        str_attributes[0].split('=')[1].strip())
    reading['power'] = float(reading_lines[1].split('=')[-1].strip())
    reading['rpm'] = int(str_attributes[1].split('=')[1].strip())

    return reading


def get_address_from_log_line(log_line: str) -> dict:
    """Takes in a kafka log line and returns a dictionary of address data from it."""

    address = {}
    address_dict = literal_eval(log_line.split('=')[1])
    if 'address' not in address_dict.keys():
        address['first_line'] = None
        address['second_line'] = None
        address['city'] = None
        address['postcode'] = None
        return address

    address_string = address_dict['address']
    address_lines = address_string.split(',')
    address['first_line'] = address_lines[0].strip()
    address['city'] = address_lines[-2].strip()
    address['postcode'] = address_lines[-1].strip()

    if len(address_lines) == 4:
        address['second_line'] = address_lines[1].strip()
    else:
        address['second_line'] = None
    return address


if __name__ == "__main__":
    pass
