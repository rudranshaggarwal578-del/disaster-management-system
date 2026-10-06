import pandas as pd

def get_disaster_data(db):
    query = """
        SELECT
            id,
            disaster_type,
            severity,
            status,
            location,
            created_at,
            verified_at,
            resolved_at
        FROM disasters
        ORDER BY created_at DESC
    """

    rows = db.execute(query).fetchall()

    data = [dict(row) for row in rows]

    return pd.DataFrame(data)

def get_summary(df):

    if df.empty:
        return {
            "total": 0,
            "reported": 0,
            "verified": 0,
            "assigned": 0,
            "responding": 0,
            "resolved": 0,
            "rejected": 0
        }

    return {
        "total": len(df),
        "reported": int((df["status"] == "Reported").sum()),
        "verified": int((df["status"] == "Verified").sum()),
        "assigned": int((df["status"] == "Assigned").sum()),
        "responding": int((df["status"] == "Responding").sum()),
        "resolved": int((df["status"] == "Resolved").sum()),
        "rejected": int((df["status"] == "Rejected").sum())
    }

def get_disaster_type_counts(df):

    if df.empty:
        return pd.DataFrame(
            columns=["disaster_type", "count"]
        )

    result = (
        df["disaster_type"]
        .value_counts()
        .reset_index()
    )

    result.columns = [
        "disaster_type",
        "count"
    ]

    return result

def get_severity_counts(df):

    if df.empty:
        return pd.DataFrame(
            columns=["severity", "count"]
        )

    result = (
        df["severity"]
        .value_counts()
        .reset_index()
    )

    result.columns = [
        "severity",
        "count"
    ]

    return result