
import duckdb
import math

con = duckdb.connect("ts.duckdb", read_only=True)

result = con.sql("""
    with moderator_7 as (
        select
            enforcement_actions,
            overturned,
            overturn_rate
        from mart_moderator_quality
        where moderator_id = 7
    ),

    other_moderators as (
        select
            sum(enforcement_actions) as enforcement_actions,
            sum(overturned) as overturned,
            sum(overturned) * 1.0 /
                nullif(sum(enforcement_actions), 0) as overturn_rate
        from mart_moderator_quality
        where moderator_id <> 7
    )

    select
        m.enforcement_actions as mod7_actions,
        m.overturned as mod7_overturned,
        m.overturn_rate as mod7_rate,
        o.enforcement_actions as other_actions,
        o.overturned as other_overturned,
        o.overturn_rate as other_rate,
        m.overturn_rate -
            o.overturn_rate as rate_difference
    from moderator_7 m
    cross join other_moderators o
""").fetchall()[0]

n7, x7, p7, no, xo, po, difference = result

se7 = math.sqrt(p7 * (1 - p7) / n7)
seo = math.sqrt(po * (1 - po) / no)
difference_se = math.sqrt(se7**2 + seo**2)

print("MODERATOR 7 VS ALL OTHER MODERATORS")
print(f"Moderator 7 enforcement actions: {n7}")
print(f"Moderator 7 overturned actions: {x7}")
print(f"Moderator 7 overturn rate: {p7:.3%}")
print(f"Moderator 7 approximate 95% CI: "
      f"{max(0, p7 - 1.96 * se7):.3%} to "
      f"{min(1, p7 + 1.96 * se7):.3%}")

print(f"\nOther moderators' enforcement actions: {no}")
print(f"Other moderators' overturned actions: {xo}")
print(f"Other moderators' pooled overturn rate: {po:.3%}")

print(f"\nDifference: {difference:.3%}")
print(f"Difference in standard errors: "
      f"{difference / difference_se:.2f}")
