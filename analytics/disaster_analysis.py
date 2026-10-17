import pandas as pd

def get_disaster_data(db):
    query = """
        SELECT
            d.id,
            d.disaster_type,
            d.ai_severity,
            da.status,
            d.location,
            d.latitude,
            d.longitude,
            d.created_at,
            d.verified_at,
            d.resolved_at,
            da.assigned_at,
            da.arrived_at,
            da.completed_at
        FROM disasters d
        LEFT JOIN disaster_assignments da
            ON d.id = da.disaster_id
        ORDER BY d.created_at DESC
    """

    rows = db.execute(query).fetchall()

    data = [dict(row) for row in rows]

    return pd.DataFrame(data)

def get_map_data(df):
    if df.empty:
        return []

    map_df = df.dropna(subset=["latitude", "longitude"])

    return map_df[
        [
            "id",
            "disaster_type",
            "ai_severity",
            "status",
            "location",
            "latitude",
            "longitude"
        ]
    ].to_dict("records")

def calculate_response_times(df):
    if df.empty:
        return df

    # Convert timestamp columns to datetime
    time_columns = [
        "created_at",
        "verified_at",
        "resolved_at",
        "assigned_at",
        "arrived_at",
        "completed_at"
    ]

    for column in time_columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    # Time taken for volunteer to reach the disaster
    df["response_time_minutes"] = (
        df["arrived_at"] - df["assigned_at"]
    ).dt.total_seconds() / 60

    # Time taken to complete the response
    df["resolution_time_minutes"] = (
        df["completed_at"] - df["arrived_at"]
    ).dt.total_seconds() / 60

    # Total time from disaster report to resolution
    df["incident_duration_minutes"] = (
        df["resolved_at"] - df["created_at"]
    ).dt.total_seconds() / 60

    return df

def get_average_times(df):
    if df.empty:
        return {
            "average_response_time": None,
            "average_resolution_time": None,
            "average_incident_duration": None
        }

    return {
        "average_response_time": df["response_time_minutes"].mean(),
        "average_resolution_time": df["resolution_time_minutes"].mean(),
        "average_incident_duration": df["incident_duration_minutes"].mean()
    }

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
            columns=["ai_severity", "count"]
        )

    result = (
        df["ai_severity"]
        .value_counts()
        .reset_index()
    )

    result.columns = [
        "ai_severity",
        "count"
    ]

    return result

