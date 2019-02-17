import gspread
from oauth2client.service_account import ServiceAccountCredentials


class Storage:
    def __init__(self, spreadsheet_key, worksheet_name, columns):
        self._scope = ['https://spreadsheets.google.com/feeds']
        self._keyfile_dict = {
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
        self._spreadsheet_key = spreadsheet_key
        self._worksheet_name = worksheet_name
        self._columns = columns

    def _get_spreadsheet(self):
        """get spreadsheet from google
        Return:
            (spreadsheet) spreadsheet class
        """
        client = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(self._keyfile_dict, self._scope))
        return client.open_by_key(self._spreadsheet_key)

    def _get_worksheet(self):
        """get worksheet from google
        Return:
            (worksheet) worksheet class
        """
        spreadsheet = self._get_spreadsheet()
        worksheet = spreadsheet.worksheet(self._worksheet_name)
        return worksheet

    def _read_worksheet(self):
        """get all rows from worksheet
        Return:
            (list) documents
                [
                    ['A1', 'B1'],
                    ['A2', 'B2'],
                    ...
                ]
        """
        worksheet = self._get_worksheet()
        return worksheet.get_all_values()

    def _delete_worksheet(self):
        """delete existed worksheet
        Return:
            (None)
        """
        spreadsheet = self._get_spreadsheet()
        worksheet = self._get_worksheet()
        spreadsheet.del_worksheet(worksheet)

    def _create_worksheet(self):
        """create empty worksheet
        Return:
            (worksheet) created worksheet
        """
        spreadsheet = self._get_spreadsheet()
        worksheet = spreadsheet.add_worksheet(title=self._worksheet_name, rows="1", cols=str(len(self._columns)))
        return worksheet

    def _write_worksheet(self, data_rows):
        """write rows into worksheet
        Args:
            (list) data_rows -- data to write to worksheet
        """
        worksheet = self._get_worksheet()
        for row in data_rows:
            worksheet.insert_row(row)
        # insert column header at last
        worksheet.insert_row(self._columns, value_input_option='USER_ENTERED')

    def read_data(self):
        """get data from googlesheet
        Return:
            (list) data rows combined with header
                [
                    ["column1", "column2", ...],
                    ...
                ]
        """
        rows = self._read_worksheet()
        return rows[1:]

    def write_data(self, data_dicts):
        """write data into googldsheet
        Args:
            (list) list of data in dict format
                [
                    {
                        "column1": "data1",
                        "column2": "data2",
                        ...
                    }
                ]
        """
        parsed_data_rows = self._convert_records_into_list(data_dicts, self._columns)
        self._delete_worksheet()
        self._create_worksheet()
        self._write_worksheet(parsed_data_rows)

    def _convert_records_into_list(self, records, columns):
        """convert records into sheet output format
        Args:
            (list) records
                [
                    {
                        "column1": "data1",
                        "column2": "data2",
                        ...
                    },
                    ...
                ]
        Returns:
            (list) output format for google sheet
                [
                    ["data1", "data2", ...],
                    ...
                ]
        """
        rows = []
        for record in records:
            row = []
            for column in columns:
                row.append(str(record[column]))
            rows.append(row)
        return rows
