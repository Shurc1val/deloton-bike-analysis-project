"""Tests the database functions work as intended. Ensures they correctly query the database."""

# pylint: disable=C0301

from unittest.mock import MagicMock,patch

from database_functions import load_rider_into_database,load_address_into_database,select_address_from_database,load_ride_into_database,select_ride_from_database,load_reading_into_database,select_reading_from_database,load_bike_into_database,select_bike_from_database
from load import add_address

EXAMPLE_USER = {'rider_id' : 1234,'address_id' : 6,'first_name': "Charlie",
                          'last_name': "Derick",'birthdate': "2002-04-13",
                          'height' : 152,'weight' : 280,'email' : "charlie@gmail.com",
                          'gender' : "male",'account_created' : "2021-09-27"}

EXAMPLE_ADDRESS = {"first_line" : "63 Studio","second_line" : "Nursery Avenue",
                   "city" : "London", "postcode" : "LA1 34A"}

EXAMPLE_RIDE = {"rider_id" : 1234, "bike_id": 1, "start_time" : "2021-07-03 16:21:12"}

EXAMPLE_READING = {"ride_id" : 1, "heart_rate" : 76, "power" : 12.6423, "rpm" : 20,
                   "resistance" : 50, "elapsed_time" : 120}

EXAMPLE_BIKE_SERIAL = "SD2e4219u"


@patch("database_functions.load_address_into_database")
def test_add_address(mock_load_address_into_database):
    """Tests the flow of adding a new dict and returning a ID functions correctly."""
    mock_db_conn = MagicMock()
    mock_load_address_into_database.return_value = 1

    assert add_address(mock_db_conn, EXAMPLE_ADDRESS) == 1


def test_load_address_into_database():
    """Tests that a address gets correctly loaded into the database"""

    mock_conn = MagicMock()

    mock_execute = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .execute
    mock_fetch = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone

    mock_fetch.return_value = (1,)

    address_id = load_address_into_database(mock_conn, EXAMPLE_ADDRESS)

    mock_execute.assert_called_once()
    mock_fetch.assert_called_once()

    assert address_id == 1


def test_select_address_from_database():
    """Tests that a address gets correctly selected from the database"""

    mock_conn = MagicMock()

    mock_execute = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .execute
    mock_fetch = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone

    mock_fetch.return_value = (1,)

    address_id = select_address_from_database(mock_conn, EXAMPLE_ADDRESS)

    mock_execute.assert_called_once()
    mock_fetch.assert_called_once()

    assert address_id == 1


def test_load_rider_into_database():
    """Tests that a rider gets correctly loaded into the database"""

    mock_conn = MagicMock()

    mock_execute = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .execute
    mock_fetch = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone

    mock_fetch.return_value = (EXAMPLE_USER["rider_id"],)

    rider_id = load_rider_into_database(mock_conn, EXAMPLE_USER)

    mock_execute.assert_called_once()
    mock_fetch.assert_called_once()

    assert rider_id == 1234


def test_load_ride_into_database():
    """Tests that a ride gets correctly loaded into the database"""

    mock_conn = MagicMock()

    mock_execute = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .execute
    mock_fetch = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone

    mock_fetch.return_value = (1,)

    ride_id = load_ride_into_database(mock_conn, EXAMPLE_RIDE)

    mock_execute.assert_called_once()
    mock_fetch.assert_called_once()

    assert ride_id == 1


def test_select_ride_from_database():
    """Tests that a ride gets correctly selected from the database"""

    mock_conn = MagicMock()

    mock_execute = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .execute
    mock_fetch = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone

    mock_fetch.return_value = (1,)

    ride_id = select_ride_from_database(mock_conn, EXAMPLE_RIDE)

    mock_execute.assert_called_once()
    mock_fetch.assert_called_once()

    assert ride_id == 1


def test_load_reading_into_database():
    """Tests that a reading gets correctly loaded into the database"""

    mock_conn = MagicMock()

    mock_execute = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .execute
    mock_fetch = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone

    mock_fetch.return_value = (1,)

    reading_id = load_reading_into_database(mock_conn, EXAMPLE_READING)

    mock_execute.assert_called_once()
    mock_fetch.assert_called_once()

    assert reading_id == 1


def test_select_reading_from_database():
    """Tests that a reading gets correctly selected from the database"""

    mock_conn = MagicMock()

    mock_execute = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .execute
    mock_fetch = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone

    mock_fetch.return_value = (1,)

    reading_id = select_reading_from_database(mock_conn, EXAMPLE_READING)

    mock_execute.assert_called_once()
    mock_fetch.assert_called_once()

    assert reading_id == 1


def test_load_bike_into_database():
    """Tests that a bike gets correctly loaded into the database"""

    mock_conn = MagicMock()

    mock_execute = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .execute
    mock_fetch = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone

    mock_fetch.return_value = (1,)

    bike_id = load_bike_into_database(mock_conn, EXAMPLE_BIKE_SERIAL)

    mock_execute.assert_called_once()
    mock_fetch.assert_called_once()

    assert bike_id == 1


def test_select_bike_from_database():
    """Tests that a bike gets correctly selected from the database"""

    mock_conn = MagicMock()

    mock_execute = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .execute
    mock_fetch = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone

    mock_fetch.return_value = (1,)

    bike_id = select_bike_from_database(mock_conn, EXAMPLE_BIKE_SERIAL)

    mock_execute.assert_called_once()
    mock_fetch.assert_called_once()

    assert bike_id == 1
