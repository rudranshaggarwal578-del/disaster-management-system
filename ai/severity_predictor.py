import joblib


model = joblib.load("ai/severity_model.pkl")


def predict_severity(disaster_type, description):
    text = disaster_type + " " + description

    prediction = model.predict([text])[0]

    probabilities = model.predict_proba([text])[0]
    confidence = max(probabilities) * 100

    return prediction, confidence