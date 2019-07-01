import googlesheet


def init(google_spreadsheet_key):
    _storage = googlesheet.Storage(google_spreadsheet_key, "configurations", None)
    _configurations = _storage.read_data()
    global key
    key = {}
    for i in _configurations:
        key[i[0]] = i[1]
