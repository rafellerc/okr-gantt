from datetime import datetime
from collections import namedtuple
from typing import List, Union, Optional, Set, Tuple
import pandas as pd


# Define structured timeline task
TimelineTask = namedtuple("TimelineTask", ["duration", "group", "task"])

def build_gantt_df(
    timeline: List[Union[TimelineTask, Tuple[int, str, str]]],
    init_date: Union[str, datetime, pd.Timestamp],
    non_workdays: Optional[Union[List[Union[str, datetime, pd.Timestamp]], Set[Union[str, datetime, pd.Timestamp]]]] = None,
    exclude_weekends: bool = True
) -> pd.DataFrame:
    """
    Build a Gantt-compatible DataFrame from a structured timeline.

    Parameters:
    - timeline: List of TimelineTask or raw tuples (duration, group, task)
    - init_date: Starting date as str, datetime, or pd.Timestamp
    - non_workdays: Optional list/set of non-working days as date-like
    - exclude_weekends: If True, excludes Saturdays and Sundays

    Returns:
    - pd.DataFrame with columns: Task, Group, Start, End
    """
    if not isinstance(init_date, pd.Timestamp):
        init_date = pd.Timestamp(init_date)

    # Normalize holidays
    non_workdays_set: Set[pd.Timestamp] = set(pd.to_datetime(non_workdays or []))

    # Cast raw tuples to TimelineTask
    typed_timeline: List[TimelineTask] = [
        task if isinstance(task, TimelineTask) else TimelineTask(*task)
        for task in timeline
    ]

    # Generate workday calendar
    max_days: int = sum(task.duration for task in typed_timeline)
    calendar = pd.date_range(start=init_date, periods=max_days * 3, freq="D")

    workdays = [
        day for day in calendar
        if (not exclude_weekends or day.weekday() < 5) and day not in non_workdays_set
    ]

    rows = []
    current_idx = 0
    for task in typed_timeline:
        start = workdays[current_idx]
        end = workdays[current_idx + task.duration - 1]
        rows.append({
            "Task": task.task,
            "Group": task.group,
            "Start": start,
            "End": end
        })
        current_idx += task.duration

    return pd.DataFrame(rows)



def build_gantt_sequence(
    timelines: List[List[Union[TimelineTask, Tuple[int, str, str]]]],
    init_date: Union[str, datetime, pd.Timestamp],
    non_workdays: Optional[Union[List[Union[str, datetime, pd.Timestamp]], Set[Union[str, datetime, pd.Timestamp]]]] = None,
    exclude_weekends: bool = True
) -> List[pd.DataFrame]:
    """
    Generate sequential Gantt DataFrames for multiple timelines, each starting after the previous one ends.

    Parameters:
    - timelines: List of individual timelines (each timeline is a list of TimelineTask or tuples)
    - init_date: Start date for the first timeline
    - non_workdays: Optional list of holiday dates
    - exclude_weekends: If True, skips weekends when assigning task days

    Returns:
    - List of pd.DataFrame, one for each timeline
    """
    current_date = pd.Timestamp(init_date)
    gantt_dfs = []

    for timeline in timelines:
        gantt_df = build_gantt_df(
            timeline=timeline,
            init_date=current_date,
            non_workdays=non_workdays,
            exclude_weekends=exclude_weekends
        )
        gantt_dfs.append(gantt_df)

        # Advance current_date to the next available workday after the last task
        last_date = gantt_df["End"].max()
        calendar = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=30, freq="D")

        non_workdays_set = set(pd.to_datetime(non_workdays or []))
        for day in calendar:
            if (not exclude_weekends or day.weekday() < 5) and day not in non_workdays_set:
                current_date = day
                break

    return gantt_dfs
