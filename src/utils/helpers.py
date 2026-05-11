def classify(score):
    if score >= 16:
        return "Excellent"
    elif score >= 10:
        return "Moyen"
    else:
        return "Faible"