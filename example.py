# ---
# jupyter:
#   jupytext:
#     custom_cell_magics: kql
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: okr
#     language: python
#     name: python3
# ---

# %%
# Example usage of OKR-style Gantt plotting tools
from datetime import datetime
from okr.plot import styled_gantt
from okr.gantt import build_gantt_sequence
from okr.workdays import get_holidays, estimate_workdays

# %%
# Define the project start date
project_start = "2025-01-06"

# %%
# Get holidays for visual accuracy (optional)
holidays = get_holidays("US", start_date=project_start, end_date="2025-03-01", subdiv="CA")

# %%
# Estimate available workdays
estimate_workdays(project_start, "2025-03-01", non_workdays=holidays.Date.to_list())

# %%
# Define multiple task timelines (Duration in workdays)
planning_tasks = [
    (2, "Planning", "Define requirements"),
    (3, "Planning", "Design system architecture"),
    (2, "Planning", "Review and approve initial specs"),
]

dev_tasks = [
    (4, "Dev", "Set up development environment"),
    (5, "Dev", "Implement core functionality"),
    (3, "Dev", "Integrate API and authentication"),
]

test_tasks = [
    (2, "QA", "Write test cases"),
    (3, "QA", "Run integration tests"),
    (2, "QA", "Fix bugs and regressions"),
]

deploy_tasks = [
    (1, "Deploy", "Prepare deployment scripts"),
    (2, "Deploy", "Deploy to staging"),
    (1, "Deploy", "Deploy to production"),
]

# %%
# Build the Gantt DataFrames
planning_df, dev_df, test_df, deploy_df = build_gantt_sequence(
    [planning_tasks, dev_tasks, test_tasks, deploy_tasks],
    init_date=project_start,
    non_workdays=holidays.Date.to_list()
)

# %%
# Plot each phase
styled_gantt(planning_df, "Phase 1: Planning", include_group_name=False)
styled_gantt(dev_df, "Phase 2: Development", include_group_name=False)
styled_gantt(test_df, "Phase 3: QA & Testing", include_group_name=False)
styled_gantt(deploy_df, "Phase 4: Deployment", include_group_name=False)

# %%
# You can also combine them into one
import pandas as pd
all_tasks = pd.concat([planning_df, dev_df, test_df, deploy_df], ignore_index=True)
styled_gantt(all_tasks, "Full Project Timeline")

# %%
