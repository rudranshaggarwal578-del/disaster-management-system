import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression


# Load training data
data = pd.read_csv("ai/severity_data.csv")


# Combine disaster type and description
data["text"] = (
    data["disaster_type"] + " " + data["description"]
)


X = data["text"]
y = data["severity"]


# Create ML pipeline
model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2)
        )
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=1000
        )
    )
])

# Train model
model.fit(X, y)

# Save trained model
joblib.dump(
    model,
    "ai/severity_model.pkl"
)

print("Severity model trained successfully!")
print("Model saved as ai/severity_model.pkl")