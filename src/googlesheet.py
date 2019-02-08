import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time


class Storage:
    def __init__(self, spreadsheet_key):
        scope = ['https://spreadsheets.google.com/feeds']
        keyfile_dict = {
            "type": "service_account",
            "project_id": "discordbot-230408",
            "private_key_id": "a03989e44342f576c115ac3006888ea929a943ac",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDeaqWZmipvDxrM\nvrSaVbx/wnYrg9H5ThsYM78D6SiQKsxiSzSqDyWbvFsbUAjdOxYWEWSKdewDGTWj\nYaZlE4N+9JEFfjOxalnZByIu4SmKxSQGxINN+K+3u9cC/d44n4WtmTGhrIqTsdnd\n4uKrmW+FR6skq1/+zqes2+o7AQsBdHq7Od3Se+vkdfLKEm6Pq89ye1UuLb2gQPkO\nHXqTxzieJTd2IUwmfetBPcaIDsKlkGdD4T8qVLm0fTtNgKc83BiKfj+ryovR5Ttw\n2Z8Iwsavix1qTtrFXw5ICj0GaD5Vj1WNrId4kWXP2YzHAL9vvLM4f9EMy+Zbvfoc\nygNhJoz/AgMBAAECggEAFODd+rVGFnbMhTvBqFsz/qo6fYs6QrTaRkNVQwC4FhBu\nbyuwHeaeGShtRPsWWe4Z/KhVT8oSBZhwOI4KGKLkTR6YHnPiVl0tYfoRc2UfiS9I\nWnpH+SHHHPA9FsLOAXK4Ebu3tP2FZKflU7bgoEse9NvtbNvJfxnXE5rxOei3J8Oi\nfXEiHcr7gGNnMg2lO7ewky9dTiJ28/MJU0yVVndeSHD3rt9T0dV3RubCTw5Qd2mz\n3GjKBSe21FR3REu7n8JDUNDxAF93dgmCMHnSoZWEWubRkq5fSGcY9QLPnjnJRUhS\nsVAJ2uGIvKsGfTuDxn1rey7isl5UqzpxCGLMSTL0gQKBgQD+d8X81O+UzNeD3ads\nMPDOSRQOz91/qACX0iyA+ScR2RGI4RwFLd3VwSBzl+w1AcwjbJoYLJg6CLIpHdcj\n7o1QFt+gQ7ArdPq2ajjfo4rr8MZoNqwGn53vOj119p9LA9Q3avyzuzP1rBi2FjDh\nMKFNT/zEBIDX7YgpEeeR7fWplwKBgQDfwXiOzxAdXD3o3uaLd9N149RyFRXF299J\nValgAqCenyhRCz3CGIe8bzfn1c9ZItgaTphx+qsFqVNpCpXgCia1A+vHogIU5gfO\nLmiw8F05mq7iFK27kFmIaYYCm4tii+wOFpa6UV1JmRxBNTkFxzadJQBPOi93OqXT\nlosHa+YU2QKBgQCSvzu8PIgVhbPbZd4BNJAKRnZ8vD7+OUJuS1RC5Gw1jLrh9v+T\ntQmzFXbDcp9TSkARRbXvrvfyr8UelQjWveFciHRaFe7ogMN8ovE9dzDMM8QXoT+/\nahlINovvFVRzjDe75cTpWVHzoVV23IE/vC2pSjF4USiEXYUiOiMTMuly7QKBgQCd\nCEC9qOAcWuIwDk8qTjwfnnc4YUfYhkicRPwLn4xuBjDbP9Jl56VLP5qyn8FXQzb6\nr3IZe9yOqpkZPQ6WH0mu/EN65V4koJOVxcg/dVFX3hEiJXUQD2xmafhc2CDoVl6i\nPIQn2nZn8oZ71Qhh37+aZZ9j+ufY+1Xputtzp+vfcQKBgQCIcqEp53UjPb8DKBmN\nizLeow6dLFDke3+wYmz7DnhBkC6vdnXaJL1xD07PGy4GLvpsVvBOOWoKCH1moTud\nL27nukxfN2ynFm9g1JSMjCkxoQiEN0bm9bwXy6cr/joRL2HWLE706yN3k0J6Si4C\nlUAe+uGjDDSXEYUJuB0u3zZ/Fw==\n-----END PRIVATE KEY-----\n",
            "client_email": "discordbot@discordbot-230408.iam.gserviceaccount.com",
            "client_id": "107385397038189452007",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/discordbot%40discordbot-230408.iam.gserviceaccount.com"
        }
        self._client = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict, scope))
        self._spreadsheet_key = spreadsheet_key
        self._spreadsheet = self._client.open_by_key(self._spreadsheet_key)
        self._users_columns = ["user_id", "points", "exp", "gm", "player", "points_used", "points_earned"]

    def _find_latest_worksheet_name(self, keyword):
        """find last worksheet with keyword
        Args:
            (str) keyword -- keyword for worksheet
        Return:
            (str) worksheet name (e.g. user_20190101_123456)
        """
        worksheets = self._spreadsheet.worksheets()
        matched_worksheet_names = [ws.title for ws in worksheets if keyword in ws.title]
        matched_worksheet_names.sort(reverse=True)
        return matched_worksheet_names[0]

    def _read_worksheet(self, sheet_name):
        """get all rows from worksheet
        Args:
            (str) sheet_name -- name of worksheet (e.g. users)
        Return:
            (list) documents
                [
                    ['A1', 'B1'],
                    ['A2', 'B2'],
                    ...
                ]
        """
        worksheet = self._spreadsheet.worksheet(sheet_name)
        return worksheet.get_all_values()

    def _create_worksheet(self, sheet_name, row_count, column_count):
        """create empty worksheet
        Args:
            (str) sheet_name -- name of worksheet (e.g. user_new)
            (int) row_count -- number of rows
            (int) column_count -- number of columns
        """
        worksheet = self._spreadsheet.add_worksheet(title=sheet_name, rows=str(row_count), cols=str(column_count))
        return worksheet

    def _write_worksheet(self, sheet_name, rows):
        """write rows into worksheet
        Args:
            (str) sheet_name -- name of worksheet (e.g. users_new)
            (list) rows -- rows to write to worksheet
        """
        worksheet = self._spreadsheet.worksheet(sheet_name)
        for row in rows:
            worksheet.insert_row(row)
        worksheet.insert_row(self._users_columns, value_input_option='USER_ENTERED')

    def read_users(self):
        """get users from googlesheet storage
        Return:
            (list) users
                [
                    {
                        "user_id": 0,
                        "points": 10,
                        "gm": 10,
                        "player": 3,
                        "points_used": 100,
                        "points_earned": 100,
                        "exp": 0
                    }
                ]
        """
        worksheet_name = self._find_latest_worksheet_name('users')
        rows = self._read_worksheet(worksheet_name)
        users = []
        for row in rows[1:]:
            user = {}
            for key, value in zip(self._users_columns, row):
                try:
                    user[key] = int(value)
                except ValueError:
                    user[key] = value
            users.append(user)
        return users

    def write_users(self, users):
        """write users to googlesheet storage
        Args:
            (list) users
                [
                    {
                        "user_id": 0,
                        "points": 10,
                        "gm": 10,
                        "player": 3,
                        "points_used": 100,
                        "points_earned": 100,
                        "exp": 0
                    }
                ]
        Return:
            (str) output worksheet name
        """
        output_users = self._convert_users_into_list(users)
        sheet_name = "users_{}".format(time.strftime("%Y%m%d_%H%M%S"))
        self._create_worksheet(sheet_name=sheet_name, row_count=len(output_users), column_count=len(self._users_columns))
        self._write_worksheet(sheet_name=sheet_name, rows=output_users)
        return sheet_name

    def _convert_users_into_list(self, users):
        """convert users into list for sheet output
        Args:
            (list) users
                [
                    {
                        "user_id": 0,
                        "points": 10,
                        "gm": 10,
                        "player": 3,
                        "points_used": 100,
                        "points_earned": 100,
                        "exp": 0
                    }
                ]
        Returns:
            (list) users
                [
                    ["user_id", "points", "exp", "gm", "player", "points_used", "points_earned"],
                    ...
                ]
        """
        rows = []
        for user in users:
            row = []
            for column in self._users_columns:
                row.append(str(user[column]))
            rows.append(row)
        return rows
