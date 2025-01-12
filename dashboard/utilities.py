"""Utility functions to transform data fetched from SQL for use in visualisations."""

# 'Unable to import' errors
# pylint: disable = E0401

from datetime import datetime, timedelta
import math

import pandas as pd


# --------------   CURRENT RIDES   -------------------
def get_current_rider_name(current_ride: list) -> str:
    """Returns a string containing the rider first and last name."""
    first_name = current_ride[1]
    last_name = current_ride[2]
    rider_name = f"{first_name} {last_name}"
    return rider_name


def get_gender_emoji(gender: str) -> str:
    """Return an emoji appropriate to the given gender."""

    if gender == "male":
        return "♂"

    if gender == "female":
        return "♀"

    return ""


def calculate_age(birthdate: datetime, current_date: datetime = datetime.utcnow()) -> int:
    """
    Returns the age in years for the given date as a datetime object
    in the format YYYY-MM-DD.
    'birthdate' is assumed to be cleaned and always as a datetime type.
    """
    age = current_date.year - birthdate.year - \
        ((current_date.month, current_date.day)
         < (birthdate.month, birthdate.day))

    return age


def calculate_max_heart_rate(user_details: list) -> int:
    """
    Returns the maximum heart rate for the given user based on their age and gender.

    'birthdate' and 'gender' are assumed to be cleaned and
    always as datetime and str types, respectively.

    'other' and 'None' gender heart rates are treated conservatively using the formula
    for females as a safety precaution.
    """
    birthdate = user_details[6]
    age = calculate_age(birthdate)
    gender = user_details[5]

    if gender in ("female", "other", None):
        return round(206 - (0.88 * age))
    if gender == "male" and age < 40:
        return round(220 - age)

    return round(208 - (0.7 * age))


def calculate_min_heart_rate(user_details: list) -> int:
    """
    Returns the minimum heart rate for the given user based on their age and gender.

    'birthdate' and 'gender' are assumed to be cleaned and
    always as datetime and str types, respectively.

    'other' and 'None' gender heart rates are treated conservatively using the formula
    for females as a safety precaution.
    """
    birthdate = user_details[6]
    age = calculate_age(birthdate)
    gender = user_details[5]

    if gender in ("female", "other", None):

        if 18 <= age <= 39:
            return 45
        if 40 <= age <= 64:
            return 52
        return 57

    # male
    if 18 <= age <= 39:
        return 40
    if 40 <= age <= 64:
        return 47

    return 52


def is_heart_rate_abnormal(user_details: list) -> bool:
    """Returns True for heart rate outside of the safe range."""

    min_heart_rate = calculate_min_heart_rate(user_details)
    max_heart_rate = calculate_max_heart_rate(user_details)
    heart_rate = user_details[7]

    return (heart_rate == 0) or not (min_heart_rate <= heart_rate <= max_heart_rate)


def get_reading_time(user_details: list) -> datetime:
    """Returns the reading time from the given user_details."""

    elapsed_time = user_details[10]
    start_time = user_details[11]

    return start_time + timedelta(seconds=elapsed_time)


def verify_reading_time(reading_time: datetime, delay: int,
                        time_now: datetime = datetime.now()) -> bool:
    """Returns True if reading time is within the allowed delay from the current time."""

    return reading_time < time_now - timedelta(seconds=delay)


# --------------   RECENT RIDES   -------------------


def round_up(reading: int, round_number: int) -> int:
    """
    Rounds the given value up to the nearest round_number for setting line chart y-axis domains.
    """
    return math.ceil(reading / float(round_number)) * round_number


def round_down(reading: int, round_number: int) -> int:
    """
    Rounds the given value down to the nearest round_number for setting line chart y-axis domains.
    """
    return math.floor(reading / float(round_number)) * round_number


def get_y_axis_domain_ends(df: pd.DataFrame, x_axis: str, y_axis: str) -> tuple:
    """
    Returns a tuple (y_min, y_max) of the given reading to use as line chart y-domain.
    """

    min_reading = df.groupby(x_axis)[
        y_axis].mean().min()
    max_reading = df.groupby(x_axis)[
        y_axis].mean().max()

    y_min = round_down(min_reading, 10)
    y_max = round_up(max_reading, 10)

    return y_min, y_max


def ceil_dt(dt, delta):
    """Round datetime up to the nearest delta minutes"""
    return dt + (datetime.min - dt) % delta


def add_age_bracket_column(df: pd.DataFrame) -> None:
    """Adds a column containing the age brackets to the given DataFrame based on the birthdate."""

    df['age'] = df['birthdate'].apply(calculate_age)

    bins = [0, 18, 25, 35, 45, 55, 65, 75, float('inf')]
    labels = ['Under 18', '18-24', '25-34',
              '35-44', '45-54', '55-64', '65-74', '75+']

    df['Age Bracket'] = pd.cut(
        df['age'], bins=bins, labels=labels, right=False, include_lowest=True)

    df.drop('age', axis=1, inplace=True)


def process_dataframe(df: pd.DataFrame, date_resolution) -> pd.DataFrame:
    """Modifies by reference the given DataFrame."""

    # Ensure elapsed time is numeric to calculate reading_time
    df['elapsed_time'] = pd.to_numeric(df['elapsed_time'])

    # Add age_bracket column
    add_age_bracket_column(df)

    # Title case genders
    df['gender'] = df['gender'].str.title()

    # Title case gender for sidebar appearance
    df.columns = [col.title() if col ==
                  'gender' else col for col in df.columns]

    # Calculate reading_time
    df["reading_time"] = df.apply(
        lambda x: (
            pd.to_datetime(x['start_time']) +
            pd.to_timedelta(x['elapsed_time'], unit='s')
        ).round('min'), axis=1)

    # Round reading time to date_resolution
    delta = timedelta(minutes=date_resolution)
    df["reading_time"] = df['reading_time'].apply(
        lambda dt: ceil_dt(dt, delta))

    return df
