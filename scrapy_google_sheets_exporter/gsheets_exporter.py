import csv
import logging
from io import TextIOWrapper

import gspread
from gspread.exceptions import NoValidUrlKeyFound
from scrapy.exceptions import NotConfigured
from scrapy.extensions.feedexport import BlockingFeedStorage, build_storage

logger = logging.getLogger(__name__)


class GoogleSheetsFeedStorage(BlockingFeedStorage):
    def __init__(self, uri, credentials, *, feed_options=None):

        self.feed_options = feed_options or {}
        self.sheet_name = self.feed_options.get("sheet_name")
        self.overwrite = self.feed_options.get("overwrite", False)
        self.fields = self.feed_options.get("fields", [])
        self.format = self.feed_options.get("format", "csv")

        if not credentials:
            raise NotConfigured(
                "Must specify GOOGLE_CREDENTIALS (dict) in the spider settings."
            )
        if not self.sheet_name:
            raise NotConfigured(
                "Must specify the sheet_name in the feed options of the FEEDS settings."
            )
        if self.format != "csv":
            raise NotConfigured(
                "This feed exporter only supports csv format. "
                f"Please update the FEEDS settings by replacing {self.format} format."
            )

        self.gc = gspread.service_account_from_dict(credentials)

        try:
            self.spreadsheet = self.gc.open_by_url(uri)
        except NoValidUrlKeyFound:
            raise NotConfigured(
                "URI provided in FEEDS is not valid. Please provide a valid URI in the format "
                "gsheets://docs.google.com/spreadsheets/d/{spreadsheet_key}"
            )

        self.sheet = self.spreadsheet.worksheet(self.sheet_name)

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
        csv_data = csv.reader(
            TextIOWrapper(file, newline="\r\n")
        )
        data_header = next(csv_data)

        header = self.fields or data_header
        if self.overwrite:
            self.sheet.clear()
            self.sheet.append_row(header)

        else:
            if self.sheet.row_values(1):
                header = self.sheet.row_values(1)
                logger.warning(
                    "FEED option 'overwrite' was set to False. Since we are appending to"
                    f"existing data, only the following fields will be exported: {header}."
                )
            else:
                self.sheet.append_row(header)

        rows = []
        for line in csv_data:
            row = dict(zip(data_header, line))
            rows.append([v for k, v in row.items() if k in header])

        self.sheet.append_rows(rows)
