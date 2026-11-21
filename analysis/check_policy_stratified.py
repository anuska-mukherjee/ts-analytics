
import duckdb
import pandas as pd

con = duckdb.connect("ts.duckdb", read_only=True)

query = """
    SELECT
        CASE
            WHEN report_date >= DATE '2026-08-15'
            THEN 'After'
            ELSE 'Before'
        END AS period,
        reason,
        COUNT(*) AS reports
    FROM fct_reports
    WHERE report_date BETWEEN DATE '2026-07-01'
                          AND DATE '2026-09-30'
    GROUP BY 1, 2
    ORDER BY 1, 2
"""

df = con.sql(query).df()
con.close()

# Report counts by category and period
counts = df.pivot(
    index="reason",
    columns="period",
    values="reports"
).fillna(0)

# Total reports in each period
totals = counts.sum(axis=0)

# Category share of all reports in each period
shares = counts.div(totals, axis=1) * 100

# Combine counts and shares
results = pd.DataFrame({
    "before_reports": counts["Before"],
    "after_reports": counts["After"],
    "before_share_pct": shares["Before"],
    "after_share_pct": shares["After"],
    "share_change_pp": shares["After"] - shares["Before"]
})

print("\n========== REPORT CATEGORY MIX SHIFT ==========")
print(results.round(2).to_string())

print("\n========== PERIOD TOTALS ==========")
print(f"Before: {int(totals['Before']):,} reports")
print(f"After:  {int(totals['After']):,} reports")

print("\n========== CATEGORY MIX INTERPRETATION ==========")
largest_shift = results["share_change_pp"].abs().idxmax()
print(
    f"Largest composition change: {largest_shift} "
    f"({results.loc[largest_shift, 'share_change_pp']:+.2f} percentage points)"
)
