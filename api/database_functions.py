"""Module containing functions used to interact with the RDS database."""

from datetime import datetime
from os import environ

from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection


load_dotenv()


def get_database_connection() -> connection:
    """Return a connection our database."""

    return psycopg2.connect(user=environ["DATABASE_USERNAME"],
                            password=environ["DATABASE_PASSWORD"],
                            host=environ["DATABASE_IP"],
                            port=environ["DATABASE_PORT"],
                            database=environ["DATABASE_NAME"]
                            )


def get_readings_by_ride_id(db_connection: connection, ride_id: int) -> list[dict]:
    """
    Returns dictionary of entries in Reading table with ride_id matching that given; returns None
    if no matches are found.
    """

    with db_connection.cursor(cursor_factory = RealDictCursor) as db_cur:

        query = """SELECT * FROM Reading WHERE ride_id=%s"""
        parameters = (ride_id,)
        db_cur.execute(query,parameters)

        reading_rows = db_cur.fetchall()

        if reading_rows:
            return [dict(row) for row in reading_rows]

        return []


def get_readings_summary_for_ride_id(db_connection: connection, ride_id: int) -> list[dict]:
    """
    Returns dictionary of attribute summaries for entries in Reading table with ride_id matching
    that given; returns None if no matches are found.
    """

    with db_connection.cursor(cursor_factory = RealDictCursor) as db_cur:

        query = """
                SELECT
                    ROUND(AVG(heart_rate), 2)::float as avg_hr,
                    ROUND(AVG(power::numeric), 2)::float as avg_power,
                    ROUND(AVG(rpm), 2)::float as avg_rpm,
                    ROUND(AVG(resistance), 2)::float as avg_resistance,
                    ROUND(MAX(elapsed_time), 2)::float as duration       
                FROM Reading
                WHERE ride_id=%s
                """
        parameters = (ride_id,)
        db_cur.execute(query,parameters)

        reading_summary = db_cur.fetchone()

        if reading_summary:
            return dict(reading_summary)

        return None


def get_ride_by_id(db_connection: connection, ride_id: int) -> dict:
    """
    Returns dictionary of entry in Ride table with ride_id matching that given; returns None if no
    matches are found.
    """

    with db_connection.cursor(cursor_factory = RealDictCursor) as db_cur:

        query = """SELECT * FROM Ride WHERE ride_id=%s"""
        parameters = (ride_id,)
        db_cur.execute(query,parameters)

        ride = db_cur.fetchone()

        if ride:
            return dict(ride)

        return None


def delete_ride_by_id(db_connection: connection, ride_id: int) -> dict:
    """
    Deletes entry in Ride table with ride_id matching that given, returning a dictionary of the
    deleted entry; returns None if no matches are found.
    """

    with db_connection.cursor(cursor_factory = RealDictCursor) as db_cur:

        query = """
            DELETE FROM Ride
            WHERE ride_id=%s
            RETURNING *
            """
        parameters = (ride_id,)
        db_cur.execute(query,parameters)

        ride = db_cur.fetchone()
        db_connection.commit()

        if ride:
            return dict(ride)

        return None


def get_rider_by_id(db_connection: connection, rider_id: int) -> dict:
    """
    Returns dictionary of the entry in Rider table with rider_id matching that given; returns None
    if no matches are found.
    """

    with db_connection.cursor(cursor_factory = RealDictCursor) as db_cur:

        query = """SELECT * FROM Rider WHERE rider_id=%s"""
        parameters = (rider_id,)
        db_cur.execute(query,parameters)

        rider = db_cur.fetchone()

        if rider:
            return dict(rider)

        return None


def get_rider_rides_by_id(db_connection: connection, rider_id: int) -> dict:
    """
    Returns list of dictionaries of the entries in the Ride table with rider_id matching that
    given; returns [] if no matches are found.
    """

    with db_connection.cursor(cursor_factory = RealDictCursor) as db_cur:

        query = """SELECT * FROM Ride WHERE rider_id=%s"""
        parameters = (rider_id,)
        db_cur.execute(query,parameters)

        ride_rows = db_cur.fetchall()

        return [dict(row) for row in ride_rows]


def get_daily_rides(db_connection: connection, date: datetime) -> dict:
    """
    Returns list of dictionaries of the entries in the Ride table with the date of the start_time
    matching that given; returns [] if no matches are found.
    """

    with db_connection.cursor(cursor_factory = RealDictCursor) as db_cur:

        query = """SELECT * FROM Ride WHERE start_time::date = %s"""
        parameters = (date,)
        db_cur.execute(query,parameters)

        ride_rows = db_cur.fetchall()

        return [dict(row) for row in ride_rows]


def get_rider_ride_num(db_connection: connection, rider_id: int) -> int:
    """
    Returns the number of rides a rider has.
    """

    with db_connection.cursor(cursor_factory = RealDictCursor) as db_cur:

        query = """SELECT COUNT(*) as num_rides FROM Ride
                    WHERE rider_id=%s"""
        parameters = (rider_id,)
        db_cur.execute(query,parameters)

        rider_ride_num = db_cur.fetchone()

        if rider_ride_num:
            return dict(rider_ride_num).get('num_rides')

        return None


def get_rider_avg_hr(db_connection: connection, rider_id: int) -> int:
    """
    Returns the avg heart rate for a rider across all their readings.
    """

    with db_connection.cursor(cursor_factory = RealDictCursor) as db_cur:

        query = """SELECT ROUND(AVG(Reading.heart_rate), 2)::float as avg_hr FROM Reading
                    JOIN Ride ON Reading.ride_id = Ride.ride_id
                    WHERE rider_id=%s"""
        parameters = (rider_id,)
        db_cur.execute(query,parameters)

        rider_hr = db_cur.fetchone()

        if rider_hr:
            return dict(rider_hr).get('avg_hr')

        return None


if __name__ == "__main__":
    db_conn = get_database_connection()
