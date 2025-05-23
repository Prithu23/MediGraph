def classify_value(value, normal_min, normal_max):
    normal_center = (normal_min + normal_max) / 2
    if normal_min <= value <= normal_max:
        return "Normal"

    percent_diff = (value / normal_center) * 100

    if percent_diff < 50:
        return "Very Low"
    elif percent_diff < 100:
        return "Low"
    elif percent_diff <= 150:
        return "High"
    else:
        return "Very High"


print(classify_value(70.1, 38, 70))