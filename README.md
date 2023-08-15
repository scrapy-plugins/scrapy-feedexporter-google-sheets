# GoogleSheets Exporter for Scrapy
[Scrapy feed export storage backend](https://doc.scrapy.org/en/latest/topics/feed-exports.html#storage-backends) for GoogleSheets.

## Requirements
-  Python 3.8+

## Installation
Install the Google Sheets Exporter for Scrapy via pip:

```bash
pip install git+https://github.com/scrapy-plugins/scrapy-feedexporter-google-sheets
```

## Usage

Follow these steps to use the Google Sheets Exporter with Scrapy:

* Add this storage backend to the Scrapy settings [FEED_STORAGES](https://docs.scrapy.org/en/latest/topics/feed-exports.html#std-setting-FEED_STORAGES) dict, as follows:

  ```python
  # settings.py
  FEED_STORAGES = {'gsheets': 'scrapy_google_sheets_exporter.gsheets_exporter.GoogleSheetsFeedStorage'}
  ```

* Configure [authentication](https://developers.google.com/identity/protocols/oauth2/service-account) by providing Google service account credentials as a dictionary in the Scrapy settings `GOOGLE_CREDENTIALS`.
  
  For example:
  ```python
  # settings.py
  GOOGLE_CREDENTIALS = { 
        "type": "service_account", 
        "project_id": "project_id here", 
        "private_key_id": "private_key_id here", 
        "private_key": "private_key here", 
        "client_email": "client@email.iam.gserviceaccount.com", 
        "client_id": "client_id here", 
        "auth_uri": "auth_uri here", 
        "token_uri": "token_uri here", 
        "auth_provider_x509_cert_url": "auth_provider_x509_cert_url here", 
        "client_x509_cert_url": "client_x509_cert_url here" 
  }
  ```
* Share the Google Sheet file with the service account's email (available in GOOGLE_CREDENTIALS as `client_email`) and give it `Editor` access.

* Configure the Scrapy settings [FEEDS](https://docs.scrapy.org/en/latest/topics/feed-exports.html#feeds) by passing the Google Sheet file URI where the feed should be exported.
  
    For example:
    ```python
    # settings.py
    FEEDS = {
        "gsheets://docs.google.com/spreadsheets/d/{spreadsheet_key}/edit#gid={worksheet_id}": {
            "format": "csv",  # mandatory
            "overwrite": True
        }
    }
    ```
  - You can get the `spreadsheet_key` and `worksheet_id` from the URL of the shared Google Sheet file
    - e.g: `https://docs.google.com/spreadsheets/d/1fWJgq5yuOdeN3YnkBZiTD0VhB1MLzBNomz0s9YwBREo/edit#gid=1261678709`
  - IMPORTANT: If the worksheet id is not provided (i.e.: there is no `/edit#gid={worksheet_id}` in the end of the URL), this exporter will export data to the **first worksheet** as default.
    
## [Feed Options](https://docs.scrapy.org/en/latest/topics/feed-exports.html#feed-options)
- This feed exporter only supports `csv` format. This setting is mandatory, there is no fallback value.
- The `overwrite` feed option (default = False) determines whether data should be appended to the existing rows in the worksheet or overwrite the data in the worksheet completely, when set to True.
- If you are using this exporter in append mode (i.e., overwrite = False), please make sure that the fields to be exported match the data already present in the worksheet. This can be achieved by passing the feed option `fields` or configuring the [FEED_EXPORT_FIELDS](https://docs.scrapy.org/en/1.7/topics/feed-exports.html#std:setting-FEED_EXPORT_FIELDS) setting.  
- If you prefer not to export the CSV headers to the worksheet (for example, when using the exporter in append mode), please include the following feed option:
  -`"item_export_kwargs": {"include_headers_line": False}`
- This exporter does not support the `batch_item_count` feed option. Instead, please use `batch_size` (number of items in each batch) if you want to insert rows in batches into the spreadsheet. Please note that the batch will be capped at a size of 2 MB, in line with Google's recommendation.



