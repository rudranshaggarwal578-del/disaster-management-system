import joblib

# Load trained model
model = joblib.load("ai/severity_model.pkl")


def predict_severity(disaster_type, description):
    text = disaster_type + " " + description

    prediction = model.predict([text])[0]

    probabilities = model.predict_proba([text])[0]
    confidence = max(probabilities) * 100

    return prediction, confidence


# Test cases
tests = [
    (
        "Flood",
        "Flood water has entered several houses and people are trapped."
    ),
    (
        "Fire",
        "Small fire in a garbage area with no injuries."
    ),
    (
        "Earthquake",
        "Major buildings have collapsed and many people are injured."
    ),
    (
        "Landslide",
        "Small rocks have fallen onto the roadside."
    )
]


for disaster_type, description in tests:

    severity, confidence = predict_severity(
        disaster_type,
        description
    )

    print("\nDisaster:", disaster_type)
    print("Description:", description)
    print("Predicted Severity:", severity)
    print("Confidence:", round(confidence, 2), "%")