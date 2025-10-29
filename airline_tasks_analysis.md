================================================================================
AIRLINE DOMAIN TASKS ANALYSIS
================================================================================

Total tasks: 50

Metric                                             Count      Percentage
--------------------------------------------------------------------------------
Tasks with nl_assertions                           50         100.0%
Tasks with communicate_info                        6          12.0%
Tasks with BOTH                                    6          12.0%
Tasks where nl_assertions is superset of communicate_info 5          10.0%
Tasks with communicate_info but NO nl_assertions   0          0.0%

================================================================================
DETAILED BREAKDOWN
================================================================================

⚠️  Tasks where communicate_info is NOT fully in nl_assertions (1):

  Task ID: 7
  communicate_info: ['1628']
  nl_assertions:
    - Agent upgrades XEHM4B to economy.
    - Agent cancels XEHM4B.
    - Agent cancels 59XX6W.
    - Agent communicates that total cost of upcoming flights is $1,628.

================================================================================
SUMMARY
================================================================================

Of the 6 tasks with both fields:
  - 5 (83.3%) have nl_assertions as superset
  - 1 (16.7%) do NOT have nl_assertions as superset

Conclusion:
  ❌ Many communicate_info values are NOT covered by nl_assertions
