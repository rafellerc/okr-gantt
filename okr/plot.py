import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta
from typing import Optional


def styled_gantt(
    df: pd.DataFrame,
    title: str,
    color_map: Optional[dict] = None,
    label_fontsize: int = 9,
    weekday_label_length: int = 3,
    max_label_length: Optional[int] = None,
    include_group_name: bool = True,
) -> None:
    """
    Render a styled Gantt chart from a timeline DataFrame.

    Parameters:
    -----------
    df : pd.DataFrame
        A DataFrame containing tasks with the following required columns:
        - 'Task': The task name (str)
        - 'Group': A group or category name (str)
        - 'Start': Start date (datetime)
        - 'End': End date (datetime)

    title : str
        Title to be displayed above the Gantt chart.

    color_map : dict, optional
        A dictionary mapping group names to matplotlib colors. If None, a default tab10 colormap is used.

    label_fontsize : int, default=9
        Font size of the task labels shown inside the task bars.

    weekday_label_length : int, default=3
        Number of characters to show for weekday names (e.g., "Mon", "Tue").
        Use -1 to display full weekday names (e.g., "Monday").

    max_label_length : int or None, default=None
        If set, truncates task labels (including group name) to at most this number of characters.

    include_group_name : bool, default=True
        Whether to prefix task labels with the group name (e.g., "[Group] Task").

    Notes:
    ------
    - The function automatically formats weekend background colors, aligns month and weekday labels,
      and spaces the chart vertically based on the number of tasks.
    - Month names appear on a secondary x-axis below the main date ticks.
    - The chart uses horizontal bars (`barh`) to show tasks spanning a number of days.

    Example:
    --------
    >>> styled_gantt(my_df, "Project Roadmap", label_fontsize=10, include_group_name=False)

    Location Codes for holidays (not used in this function but relevant for pre-processing):
    - California (US): "US-CA"
    - Brasília (Brazil): "BR-DF"
    - Vancouver (Canada): "CA-BC"
    """

    import numpy as np

    # --- Type checks ---
    if not isinstance(df, pd.DataFrame):
        raise TypeError("`df` must be a pandas DataFrame.")
    required_columns = {"Start", "End", "Group", "Task"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"`df` must contain the following columns: {required_columns}")
    if not isinstance(title, str):
        raise TypeError("`title` must be a string.")
    if color_map is not None and not isinstance(color_map, dict):
        raise TypeError("`color_map` must be a dict or None.")
    if not isinstance(label_fontsize, int):
        raise TypeError("`label_fontsize` must be an integer.")
    if not isinstance(weekday_label_length, int):
        raise TypeError("`weekday_label_length` must be an integer.")
    if max_label_length is not None and not isinstance(max_label_length, int):
        raise TypeError("`max_label_length` must be an integer or None.")
    if not isinstance(include_group_name, bool):
        raise TypeError("`include_group_name` must be a boolean.")

    # --- Setup figure ---
    fig_height = max(len(df) * 0.5, 3)
    fig, ax = plt.subplots(figsize=(16, fig_height))


    # Color mapping
    groups = df["Group"].unique()
    cmap = plt.get_cmap("tab10")
    group_colors = color_map or {group: cmap(i % 10) for i, group in enumerate(groups)}

    # Ensure datetime format
    df["Start"] = pd.to_datetime(df["Start"])
    df["End"] = pd.to_datetime(df["End"])

    # Compute date range and midpoint
    date_min = df["Start"].min()
    date_max = df["End"].max()
    midpoint_date = date_min + (date_max - date_min) / 2
    all_days = pd.date_range(date_min, date_max, freq='D')

    # Background shading per day
    for day in all_days:
        color = "#f0f0f0" if day.weekday() < 5 else "#e0e0e0"
        ax.axvspan(day, day + timedelta(days=1), color=color, alpha=0.5, zorder=0)

    # Generate month ticks, ensuring the first visible month label is at the first visible day
    months = pd.date_range(date_min.replace(day=1), date_max, freq="MS")
    month_ticks = [date_min] + [m for m in months if m > date_min]
    month_labels = [date_min.strftime("%B")] + [m.strftime("%B") for m in months if m > date_min]

    # Plot month divider lines at the actual month boundaries
    for month in months:
        ax.axvline(month, color="black", linestyle="--", linewidth=0.7)

    # Add secondary x-axis below for month names
    month_ax = ax.secondary_xaxis("bottom")
    month_ax.set_xlim(ax.get_xlim())
    month_ax.set_xticks(month_ticks)
    month_ax.set_xticklabels(month_labels, fontsize=12)
    month_ax.spines['bottom'].set_visible(False)
    month_ax.tick_params(axis='x', length=0, pad=25)

    # Align and color month labels
    for tick in month_ax.get_xticklabels():
        tick.set_horizontalalignment("left")
        tick.set_color("black")  # <<< this changes the month label color

    # Plot bars and task labels
    for i, row in df.iterrows():
        start = row["Start"]
        end = row["End"]
        width = (end - start).days + 1
        color = group_colors[row["Group"]]
        # Base bar: full task span
        ax.barh(y=i, width=width, left=start, height=0.6,
                color=color, alpha=0.6, edgecolor="black", zorder=1)

        # Overlay semi-transparent gray on weekend slices
        task_days = pd.date_range(start=start, end=end, freq="D")
        for day in task_days:
            if day.weekday() >= 5:  # Saturday or Sunday
                ax.barh(y=i, width=1, left=day, height=0.6,
                        color='white', alpha=0.4, edgecolor=None, zorder=2)

        label_core = row["Task"]
        if include_group_name:
            label = f"[{row['Group']}] {label_core}"
        else:
            label = label_core

        if max_label_length is not None and len(label) > max_label_length:
            label = label[:max_label_length - 1] + "…"

        # Alignment logic
        if start <= midpoint_date:
            label_x = start + timedelta(days=0.1)
            align = 'left'
        else:
            label_x = end + timedelta(days=0.9)
            align = 'right'

        ax.text(label_x, i, label,
                va='center', ha=align, fontsize=label_fontsize, color='black')

    # X-axis: days
    ax.set_xlim(date_min - timedelta(days=1), date_max + timedelta(days=2))
    ax.set_title(title)
    ax.set_xticks(all_days)
    ax.set_xticklabels([d.strftime('%d') for d in all_days])
    ax.tick_params(axis='x', labelrotation=0, pad=8, labelsize=8)
    for day, label in zip(all_days, ax.get_xticklabels()):
        label.set_horizontalalignment('left')
        if day.weekday() >= 5:
            label.set_color("gray")

    # Top axis: weekday names
    def format_weekday(day: pd.Timestamp) -> str:
        name = day.strftime('%A')
        return name if weekday_label_length == -1 else name[:weekday_label_length]

    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks(all_days)
    ax2.set_xticklabels([format_weekday(d) for d in all_days])
    ax2.tick_params(axis='x', pad=0, labelsize=8, length=0)
    for day, label in zip(all_days, ax2.get_xticklabels()):
        label.set_horizontalalignment('left')
        if day.weekday() >= 5:
            label.set_color("gray")

    # Y-axis cleanup
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_ylim(-0.5, len(df) - 0.5)
    ax.invert_yaxis()

    plt.grid(True, axis='x', linestyle="--", linewidth=0.3)
    plt.tight_layout()
    plt.show()