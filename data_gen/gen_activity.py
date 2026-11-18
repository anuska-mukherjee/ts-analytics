import numpy as np
import pandas as pd

from data_gen import config as c

rng = np.random.default_rng(c.SEED + 1)
start = pd.Timestamp(c.START_DATE)
end = start + pd.Timedelta(days=c.N_DAYS)
policy_day = start + pd.Timedelta(days=c.POLICY_CHANGE_DAY)
STRICT_MOD = 7  # the over-enforcing moderator

users = pd.read_csv(f"{c.RAW_DIR}/users.csv", parse_dates=["created_at"])
truth = pd.read_csv(f"{c.TRUTH_DIR}/users_truth.csv")
u = users.merge(truth, on="user_id")
N = len(u)
all_ids = u.user_id.values

# ---------- MODERATORS ----------
moderators = pd.DataFrame(
    {
        "moderator_id": np.arange(1, c.N_MODERATORS + 1),
        "team": rng.choice(["fraud", "content", "general"], size=c.N_MODERATORS),
        "hired_at": start - pd.to_timedelta(rng.integers(30, 900, size=c.N_MODERATORS), unit="D"),
    }
)

# ---------- MESSAGES ----------
TEXTS = {
    "normal": ["Is this still available?", "Can you do a lower price?", "Thanks, received the item!",
               "What time can we meet?", "Does it come with the box?"],
    "spam": ["Visit my page for cheap deals!!! click here", "BUY NOW limited offer www.deal-spam.example",
             "Follow me for free gift cards"],
    "scam": ["Pay me outside the app, send gift card codes", "Send a deposit first by wire, I will ship tomorrow",
             "Your account is locked, verify at secure-login.example"],
    "harassment": ["You are useless, nobody wants your junk", "I will keep messaging you until you reply",
                   "Stupid seller, you deserve bad reviews"],
}


def build_messages(group, counts, window_fn, kind_fn):
    sender = np.repeat(group.user_id.values, counts)
    created = pd.DatetimeIndex(np.repeat(group.created_at.values, counts))
    remaining = np.asarray((end - created).total_seconds())
    offs = np.minimum(window_fn(len(sender), remaining), remaining)
    return pd.DataFrame(
        {
            "sender_id": sender,
            "sent_at": created + pd.to_timedelta(offs, unit="s"),
            "kind": kind_fn(len(sender)),
            "archetype": group.archetype.iloc[0],
        }
    )


def grp(name):
    return u[u.archetype == name]


g_norm, g_spam, g_ring, g_rep = grp("normal"), grp("spam_burst"), grp("ring"), grp("repeat_offender")

parts = [
    build_messages(g_norm, rng.poisson(5, len(g_norm)),
                   lambda n, rem: rng.random(n) * rem, lambda n: np.full(n, "normal")),
    build_messages(g_spam, rng.integers(50, 81, len(g_spam)),
                   lambda n, rem: rng.random(n) * 3600, lambda n: np.full(n, "spam")),
    build_messages(g_ring, rng.integers(20, 41, len(g_ring)),
                   lambda n, rem: rng.random(n) * 10 * 86400, lambda n: np.full(n, "scam")),
    build_messages(g_rep, rng.integers(25, 36, len(g_rep)),
                   lambda n, rem: rng.random(n) * rem,
                   lambda n: rng.choice(["harassment", "normal"], size=n, p=[0.6, 0.4])),
]

msgs = pd.concat(parts).sort_values("sent_at").reset_index(drop=True)
msgs["message_id"] = msgs.index + 1
msgs["is_violating"] = msgs.kind != "normal"

receiver = rng.choice(all_ids, size=len(msgs))
msgs["receiver_id"] = np.where(receiver == msgs.sender_id.values, receiver % N + 1, receiver)

msgs["text"] = ""
for kind, texts in TEXTS.items():
    m = msgs.kind == kind
    msgs.loc[m, "text"] = rng.choice(texts, size=m.sum())

# ---------- REPORTS ----------
viol_p = msgs.archetype.map({"spam_burst": 0.08, "ring": 0.4, "repeat_offender": 0.4}).fillna(0.0)
p = np.where(msgs.is_violating, viol_p, 0.02)            # 2% of normal messages get falsely reported
p = p * np.where(msgs.sent_at >= policy_day, 1.25, 1.0)  # policy change: more reports
rep = msgs[rng.random(len(msgs)) < p].copy()

reporter = rng.choice(all_ids, size=len(rep))
rep["reporter_id"] = np.where(reporter == rep.sender_id.values, reporter % N + 1, reporter)
rep["created_at"] = rep.sent_at + pd.to_timedelta(rng.exponential(6 * 3600, len(rep)), unit="s")
rep["reason"] = np.where(rep.is_violating, rep.kind, rng.choice(["spam", "scam", "harassment"], size=len(rep)))
rep = rep.sort_values("created_at").reset_index(drop=True)
rep["report_id"] = rep.index + 1

# ---------- MODERATION ACTIONS ----------
rev = rep[rng.random(len(rep)) < 0.9].copy()  # 10% of reports are never reviewed

w = np.ones(c.N_MODERATORS)
w[STRICT_MOD - 1] = 3  # the strict moderator handles more cases
rev["moderator_id"] = rng.choice(np.arange(1, c.N_MODERATORS + 1), size=len(rev), p=w / w.sum())

x = rng.random(len(rev))
strict = (rev.moderator_id == STRICT_MOD).values
valid = rev.is_violating.values
rev["action_type"] = np.where(
    valid,
    np.where(x < 0.6, "remove_content", np.where(x < 0.85, "warn", "suspend")),
    np.where(strict,
             np.where(x < 0.6, "remove_content", "warn"),          # strict mod acts on innocent reports
             np.where(x < 0.85, "no_action", "warn")),
)

hours = rng.lognormal(np.log(8), 0.9, len(rev))
hours = hours * np.where(rev.created_at >= policy_day, 1.5, 1.0)  # queue slows after policy change
rev["actioned_at"] = rev.created_at + pd.to_timedelta(hours, unit="h")
rev = rev.sort_values("actioned_at").reset_index(drop=True)
rev["action_id"] = rev.index + 1

# ---------- APPEALS ----------
acted = rev[rev.action_type != "no_action"].copy()
appealed = acted[rng.random(len(acted)) < np.where(acted.is_violating, 0.2, 0.5)].copy()
overturned = rng.random(len(appealed)) < np.where(appealed.is_violating, 0.05, 0.8)
appeal_created = appealed.actioned_at.values + pd.to_timedelta(rng.uniform(1, 48, len(appealed)), unit="h").values
appeal_resolved = appeal_created + pd.to_timedelta(rng.uniform(1, 72, len(appealed)), unit="h").values

appeals = pd.DataFrame(
    {
        "appeal_id": np.arange(1, len(appealed) + 1),
        "action_id": appealed.action_id.values,
        "user_id": appealed.sender_id.values,
        "created_at": appeal_created,
        "outcome": np.where(overturned, "overturned", "upheld"),
        "resolved_at": appeal_resolved,
    }
)

# ---------- SAVE ----------
moderators.to_csv(f"{c.RAW_DIR}/moderators.csv", index=False)
msgs[["message_id", "sender_id", "receiver_id", "sent_at", "text"]].to_csv(f"{c.RAW_DIR}/messages.csv", index=False)
rep[["report_id", "reporter_id", "sender_id", "message_id", "reason", "created_at"]] \
    .rename(columns={"sender_id": "target_user_id"}).to_csv(f"{c.RAW_DIR}/reports.csv", index=False)
rev[["action_id", "report_id", "moderator_id", "action_type", "actioned_at"]] \
    .to_csv(f"{c.RAW_DIR}/moderation_actions.csv", index=False)
appeals.to_csv(f"{c.RAW_DIR}/appeals.csv", index=False)

# answer keys (never shown to dbt)
msgs[["message_id", "kind", "is_violating"]].to_csv(f"{c.TRUTH_DIR}/messages_truth.csv", index=False)
rep[["report_id", "is_violating"]].rename(columns={"is_violating": "is_valid"}) \
    .to_csv(f"{c.TRUTH_DIR}/reports_truth.csv", index=False)

# ---------- QUICK SELF-CHECK ----------
acted["overturned"] = False
acted.loc[appealed.index, "overturned"] = overturned
days_before = c.POLICY_CHANGE_DAY
days_after = c.N_DAYS - c.POLICY_CHANGE_DAY
print("messages:", len(msgs), "| reports:", len(rep), "| actions:", len(rev), "| appeals:", len(appeals))
print("share of reports about repeat offenders:", round((rep.archetype == "repeat_offender").mean(), 2))
print("reports/day before policy change:", round((rep.created_at < policy_day).sum() / days_before))
print("reports/day after policy change: ", round((rep.created_at >= policy_day).sum() / days_after))
print("overturn rate (strict mod vs others):")
print(acted.groupby(acted.moderator_id == STRICT_MOD).overturned.mean().round(3))