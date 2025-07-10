import holidays
from datetime import date
import pandas as pd
from typing import Optional, Iterable


def get_holidays(
    country_code: str,
    start_date: str,
    end_date: str,
    subdiv: Optional[str] = None
) -> pd.DataFrame:
    """
    Returns a DataFrame of holidays for a given country and date interval.

    Args:
        country_code (str): ISO 3166 country code. Examples:
            - 'US' for United States
            - 'BR' for Brazil
            - 'CA' for Canada

        start_date (str): Start date in 'YYYY-MM-DD'.
        end_date (str): End date in 'YYYY-MM-DD'.

        subdiv (str, optional): Subdivision for state/province-level holidays.
            Common options:
            - 'CA' (with country='US'): California, USA
            - 'DF' (with country='BR'): Distrito Federal (Brasília), Brazil
            - 'BC' (with country='CA'): British Columbia (includes Vancouver), Canada

    Returns:
        pd.DataFrame: A table with columns:
            - 'Date': The holiday date
            - 'Holiday': The name of the holiday
    """
    start = pd.to_datetime(start_date).date()
    end = pd.to_datetime(end_date).date()
    years = list(range(start.year, end.year + 1))

    holiday_list = holidays.country_holidays(
        country=country_code,
        subdiv=subdiv,
        years=years
    )

    holidays_in_range = {
        day: name for day, name in holiday_list.items()
        if start <= day <= end
    }

    return pd.DataFrame({
        "Date": holidays_in_range.keys(),
        "Holiday": holidays_in_range.values()
    }).sort_values("Date").reset_index(drop=True)


def estimate_workdays(
    start_date: str,
    end_date: str,
    non_workdays: Optional[Iterable[date]] = None
) -> int:
    """
    Estimates the number of workdays (weekdays excluding weekends and holidays)
    between two dates (inclusive).

    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        non_workdays (Optional[Iterable[date]]): A list or set of dates (datetime.date)
            that should be excluded as non-working days (e.g., public holidays).

    Returns:
        int: Number of estimated workdays in the interval.
    """
    start = pd.to_datetime(start_date).date()
    end = pd.to_datetime(end_date).date()

    all_days = pd.date_range(start=start, end=end, freq='D')
    weekdays = all_days[all_days.weekday < 5]  # Monday–Friday only

    if non_workdays:
        holidays_set = set(non_workdays)
        workdays = [day for day in weekdays if day.date() not in holidays_set]
    else:
        workdays = weekdays

    return len(workdays)
