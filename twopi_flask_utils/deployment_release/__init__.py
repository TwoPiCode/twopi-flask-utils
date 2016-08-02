def get_release():
    try:
        with open('version.txt') as fh:
            return fh.read().strip()
    except Exception:
        return '__UNKNOWN__'
