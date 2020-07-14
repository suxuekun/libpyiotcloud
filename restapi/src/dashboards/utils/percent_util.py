def get_percent_by(value, max):
    try:
        return round(float(value) * 100 / float(max), 2)
    except Exception as e:
        return 0