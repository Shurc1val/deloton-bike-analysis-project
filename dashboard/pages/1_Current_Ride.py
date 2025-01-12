"""
Dashboard script for the current ride to establish connection to the RDS database,
fetch data using SQL queries and create visualisations in a Streamlit app
using functions from the `database.py`, `visualisations.py` and `utilities.pyz files as necessary.
"""

# 'Unable to import' errors
# pylint: disable = E0401

from datetime import datetime
import time

from dotenv import load_dotenv
from psycopg2 import extensions
import streamlit as st

from database import (get_database_connection,
                      get_current_ride_data, get_current_ride_data_highest)
from utilities import (get_current_rider_name, verify_reading_time,
                       is_heart_rate_abnormal, get_reading_time)
from visualisations import (get_current_ride_header, get_current_rider_info_header,
                            get_personal_info_subheader, get_personal_best_subheader,
                            get_current_ride_header_personal_info, get_current_ride_metrics,
                            get_current_ride_personal_best_metrics, get_last_updated_current_ride,
                            get_heart_rate_warning)


CURRENT_RIDE_REFRESH_RATE = 1
LAST_UPDATED_COUNT_INCREMENT = 1
READING_TIME_LAG_DELAY = 30


def main_current_ride(db_connection: extensions.connection) -> None:
    """
    Main function that calls all the functions related to
    displaying the current ride visualisations.
    """

    current_ride = get_current_ride_data(db_connection)

    if not current_ride:
        st.header("⚠️ Bike not in use.")
        return

    current_ride_personal_best = get_current_ride_data_highest(
        db_connection, current_ride)

    with st.container():

        reading_time = get_reading_time(current_ride)

        if verify_reading_time(reading_time, READING_TIME_LAG_DELAY):
            st.header("⚠️ Bike not in use.")

        else:

            rider_name = get_current_rider_name(current_ride)

            get_current_ride_header(rider_name)

            get_current_ride_metrics(current_ride)

            # readings to monitor for heart rate warning
            heart_rate = current_ride[7]
            elapsed_time = current_ride[10]

            if is_heart_rate_abnormal(current_ride) and elapsed_time > 10:
                get_heart_rate_warning(heart_rate)

            get_personal_info_subheader()

            get_current_ride_header_personal_info(current_ride)

            get_personal_best_subheader()

            get_current_ride_personal_best_metrics(current_ride_personal_best)


if __name__ == "__main__":

    st.set_page_config(
        page_title="Current Rides",
        page_icon="🚲",
        layout="wide"
    )

    load_dotenv()

    conn = get_database_connection()

    while True:
        # Auto-refresh the current ride section
        main_current_ride(conn)

        for i in range(CURRENT_RIDE_REFRESH_RATE):
            time.sleep(LAST_UPDATED_COUNT_INCREMENT)

        st.rerun()
