import csv
import logging
from io import StringIO

import gspread
from scrapy.exceptions import NotConfigured
from scrapy.extensions.feedexport import BlockingFeedStorage, build_storage

logger = logging.getLogger(__name__)


class GoogleSheetsFeedStorage(BlockingFeedStorage):
    def __init__(self, uri, credentials, *, feed_options=None):
        if credentials:
            self.gc = gspread.service_account_from_dict(credentials)
        else:
            raise NotConfigured(
                "Must specify GOOGLE_CREDENTIALS (dict) in the spider settings."
            )

        self.spreadsheet_key, self.sheet_name = self.parse_gsheets_uri(uri)
        self.spreadsheet = self.gc.open_by_key(self.spreadsheet_key)
        self.sheet = self.spreadsheet.worksheet(self.sheet_name)
        self.feed_options = feed_options or {}
        self.append_mode = self.feed_options.get("append_mode", False)
        self.fields = self.feed_options.get("fields", [])
        self.format = self.feed_options.get("format", "csv")

        if self.format != "csv":
            raise NotConfigured(
                "This feed exporter only supports csv format. "
                f"Please update the FEEDS settings by replacing {self.format} format."
            )

    @classmethod
    def from_crawler(cls, crawler, uri, *, feed_options=None):
        return build_storage(
            cls,
            uri,
            credentials=crawler.settings["GOOGLE_CREDENTIALS"],
            feed_options=feed_options,
        )

    def _store_in_thread(self, file):
        file.seek(0)
        csv_text = file.read().decode("utf-8")
        csv_reader = csv.reader(StringIO(csv_text))
        csv_data = list(csv_reader)

        items = [dict(zip(csv_data[0], item)) for item in csv_data[1:]]

        header = self.fields or csv_data[0]
        if not self.append_mode:
            self.sheet.clear()
            self.sheet.append_row(header)

        else:
            if self.sheet.row_values(1):
                header = self.sheet.row_values(1)
                logger.warning(
                    "FEED option 'append_mode' was set to True. "
                    f"The following fields will be exported: {header}."
                )
            else:
                self.sheet.append_row(header)

        for item in items:
            row = [item.get(field) for field in header]
            self.sheet.append_row(row)

    @staticmethod
    def parse_gsheets_uri(uri):
        parsed_uri = uri.split("//")[-1].split("/")
        if len(parsed_uri) >= 2:
            return parsed_uri[:2]
        raise Exception(
            "Invalid Google Sheets URI. Please provide URI with this format in FEEDS: "
            "'gsheets://{spreadsheet_key}/{worksheet_name}'"
        )
