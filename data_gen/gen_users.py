
import os
import numpy as np
import pandas as pd
from faker import Faker

from data_gen import config as c


# ---------- OUTPUT DIRECTORY SETUP ----------
os.makedirs(c.RAW_DIR, exist_ok=True)
os.makedirs(c.TRUTH_DIR, exist_ok=True)


# ---------- REPRODUCIBILITY ----------
rng = np.random.default_rng(c.SEED)

fake = Faker()
Faker.seed(c.SEED)

n = c.N_USERS
start = pd.Timestamp(c.START_DATE)


# ---------- USER PROFILE GENERATION ----------
day_offset = rng.integers(0, c.N_DAYS, size=n)
sec_offset = rng.integers(0, 86_400, size=n)

created_at = (
    start
    + pd.to_timedelta(day_offset, unit="D")
    + pd.to_timedelta(sec_offset, unit="s")
)

users = pd.DataFrame(
    {
        "user_id": np.arange(1, n + 1),
        "email": [
            f"{fake.user_name()}{i}@{fake.free_email_domain()}"
            for i in range(1, n + 1)
        ],
        "country": rng.choice(
            ["US", "UK", "IN", "DE", "BR", "CA"],
            size=n,
            p=[0.35, 0.15, 0.20, 0.10, 0.10, 0.10],
        ),
        "signup_ip": [fake.ipv4() for _ in range(n)],
        "created_at": created_at,
    }
)


# ---------- GROUND-TRUTH CLASSIFICATION ----------
# Ground-truth labels are maintained separately from analytical datasets.
# They are reserved exclusively for model evaluation and validation.

truth = pd.DataFrame(
    {
        "user_id": users.user_id,
        "archetype": "normal",
    }
)


# ---------- DEFAULTER COHORT 1: COORDINATED ACCOUNT NETWORK ----------
# Simulate a coordinated group of accounts exhibiting shared
# infrastructure, including common signup IP addresses and devices.

ring_ids = rng.choice(
    users.user_id.values,
    size=c.RING_SIZE,
    replace=False,
)

ring_start = start + pd.Timedelta(days=c.RING_START_DAY)
ring_ips = [
    fake.ipv4()
    for _ in range(c.RING_IPS)
]

is_ring = users.user_id.isin(ring_ids)

users.loc[is_ring, "created_at"] = [
    ring_start + pd.Timedelta(seconds=int(s))
    for s in rng.integers(
        0,
        c.RING_WINDOW_DAYS * 86_400,
        size=c.RING_SIZE,
    )
]

users.loc[is_ring, "signup_ip"] = rng.choice(
    ring_ips,
    size=c.RING_SIZE,
)

truth.loc[is_ring, "archetype"] = "ring"


# ---------- DEFAULTER COHORT 2: REPEAT POLICY VIOLATORS ----------
# Simulate accounts with recurring policy violations.
# These accounts are excluded from the coordinated network cohort.

pool = users.loc[
    ~is_ring,
    "user_id"
].values

n_rep = int(n * c.REPEAT_OFFENDER_SHARE)

rep_ids = rng.choice(
    pool,
    size=n_rep,
    replace=False,
)

truth.loc[
    truth.user_id.isin(rep_ids),
    "archetype",
] = "repeat_offender"


# ---------- DEFAULTER COHORT 3: SPAM ACTIVITY PATTERNS ----------
# Simulate accounts exhibiting concentrated bursts of spam activity.
# These accounts are mutually exclusive from the other defaulter cohorts.

pool = truth.loc[
    truth.archetype == "normal",
    "user_id"
].values

n_spam = int(n * c.SPAMMER_SHARE)

spam_ids = rng.choice(
    pool,
    size=n_spam,
    replace=False,
)

truth.loc[
    truth.user_id.isin(spam_ids),
    "archetype",
] = "spam_burst"


# ---------- DEVICE ASSOCIATION GENERATION ----------
# Generate device associations representing individual usage,
# legitimate household sharing, and coordinated account infrastructure.

ring_devices = [
    f"dev_ring_{i}"
    for i in range(c.RING_DEVICES)
]

rows = []
dev_counter = 0
prev_device = None

users_sorted = users.sort_values("created_at")

# Precompute the coordinated network membership set for efficient lookups.
ring_set = set(ring_ids)

for uid, ts in zip(
    users_sorted.user_id,
    users_sorted.created_at,
):

    # Assign coordinated network members to shared infrastructure.
    if uid in ring_set:
        rows.append(
            (uid, rng.choice(ring_devices), ts)
        )
        continue

    # Simulate legitimate household device sharing.
    if prev_device and rng.random() < c.FAMILY_SHARE:
        rows.append(
            (uid, prev_device, ts)
        )
        continue

    # Generate one or two devices for individual accounts.
    n_dev = 1 if rng.random() < 0.8 else 2

    for _ in range(n_dev):
        dev_counter += 1

        dev = f"dev_{dev_counter:06d}"

        rows.append(
            (uid, dev, ts)
        )

        prev_device = dev


devices = pd.DataFrame(
    rows,
    columns=[
        "user_id",
        "device_id",
        "first_seen_at",
    ],
)


# ---------- DATASET EXPORT ----------
# Export analytical datasets separately from ground-truth labels.

users.to_csv(
    f"{c.RAW_DIR}/users.csv",
)

devices.to_csv(
    f"{c.RAW_DIR}/devices.csv",
    index=False,
)

truth.to_csv(
    f"{c.TRUTH_DIR}/users_truth.csv",
    index=False,
)


# ---------- GENERATION SUMMARY ----------
print("\n========== DATA GENERATION SUMMARY ==========")

print(f"Total user records: {len(users):,}")
print(f"Total device associations: {len(devices):,}")

print("\nGround-truth cohort distribution:")

print(
    truth["archetype"]
    .value_counts()
    .to_string()
)

print("\nGenerated files:")
print(f"- {c.RAW_DIR}/users.csv")
print(f"- {c.RAW_DIR}/devices.csv")
print(f"- {c.TRUTH_DIR}/users_truth.csv")

print("\n==============================================")
