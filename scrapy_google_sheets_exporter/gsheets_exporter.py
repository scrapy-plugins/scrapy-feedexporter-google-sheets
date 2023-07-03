import csv
import logging
from io import TextIOWrapper
from urllib.parse import parse_qs, urlparse

import gspread
from gspread.exceptions import NoValidUrlKeyFound
from scrapy.exceptions import NotConfigured
from scrapy.extensions.feedexport import BlockingFeedStorage, build_storage

logger = logging.getLogger(__name__)


class GoogleSheetsFeedStorage(BlockingFeedStorage):
    def __init__(self, uri, credentials, *, feed_options=None):

        self.feed_options = feed_options or {}
        self.overwrite = self.feed_options.get("overwrite", False)
        self.format = self.feed_options.get("format", "csv")
        self.batch_size = self.feed_options.get("batch_size", 0)
        self.max_payload_size = 2 * 1024 * 1024  # 2 MB as recommended by Google

        if not credentials:
            raise NotConfigured(
                "Must specify GOOGLE_CREDENTIALS (dict) in the spider settings."
            )
        if self.format != "csv":
            raise NotConfigured(
                "This feed exporter only supports csv format. "
                f"Please update the FEEDS setting, replacing {self.format} format with csv."
            )

        self.gc = gspread.service_account_from_dict(credentials)

        try:
            self.spreadsheet = self.gc.open_by_url(uri)
        except NoValidUrlKeyFound:
            raise NotConfigured(
                "URI provided in FEEDS setting is not valid. Please provide a valid URI in the format "
                "gsheets://docs.google.com/spreadsheets/d/{spreadsheet_key}/edit#gid={worksheet_id}"
            )

        self.sheet = self._parse_and_select_sheet(uri, self.spreadsheet)

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
            TextIOWrapper(file)
        )
        if self.overwrite:
            self.sheet.clear()

        batch = []
        payload_size = 0
        for row in csv_data:
            row_size = sum(len(cell.encode('utf-8')) for cell in row)
            batch.append(row)
            payload_size += row_size
            if payload_size >= self.max_payload_size or \
                    len(batch) >= self.batch_size:
                self.sheet.append_rows(batch)
                payload_size = 0
                batch = []

        # remaining batch
        if batch:
            self.sheet.append_rows(batch)

    @staticmethod
    def _parse_and_select_sheet(uri, spreadsheet):
        parsed_url = parse_qs(urlparse(uri).fragment)
        sheet_id = parsed_url.get("gid", [None])[0]

        if not sheet_id:
            logger.warning(
                f"Not able to parse worksheet id from {uri}, please make sure to match format "
                "gsheets://docs.google.com/spreadsheets/d/{spreadsheet_key}/edit#gid={worksheet_id}."
            )

        for sheet in spreadsheet.worksheets():
            if str(sheet.id) == str(sheet_id):
                return sheet

        sheet = spreadsheet.get_worksheet(0)
        logger.warning(
            f"Not able to find worksheet with id {sheet_id} in {uri}, "
            f"using first worksheet to export data instead: {sheet.title}."
        )
        return sheet
