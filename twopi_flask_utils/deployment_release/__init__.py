def get_release():
    """
    Opens a file ``version.txt`` and returns it's stripped contents.
    
    :returns: The stripped file contents
    """
    try:
        with open('version.txt') as fh:
            return fh.read().strip()
    except Exception:
        return '__UNKNOWN__'
