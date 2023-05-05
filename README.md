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

* Add this storage backend to the Scrapy settings [FEED_STORAGES](https://docs.scrapy.org/en/latest/topics/feed-exports.html#std-setting-FEED_STORAGES), as follows:

  ```python
  # settings.py
  FEED_STORAGES = {'gsheets': 'scrapy_google_sheets_exporter.gsheets_exporter.GoogleSheetsFeedStorage'}
  ```

* Configure [authentication](https://developers.google.com/identity/protocols/oauth2/service-account) by passing the Google service account credentials as a dictionary in the Scrapy settings.
  
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

* Configure the Scrapy settings [FEEDS](https://docs.scrapy.org/en/latest/topics/feed-exports.html#feeds) by passing the key and worksheet name where the feed needs to be exported.
  
    For example:
    ```python
    # settings.py
    FEEDS = {
        "gsheets://{spreadsheet_key}/{worksheet_name}": {
            "format": "csv",
            "overwrite": True
        }
    }
    ```
  - You can get the `spreadsheet_key` from the URL of the shared Google Sheet file. It's the long string of characters after `/d/` and before `/edit`
    - e.g: `https://docs.google.com/spreadsheets/d/{spreadsheet_key}/edit#gid=0`
    
## Feed Options
- Currently, this feed exporter only supports `csv` format. 
- The `overwrite` [feed option](https://docs.scrapy.org/en/latest/topics/feed-exports.html#feed-options) controls whether to append data to the end rows of the Google Sheet or overwrite it completely. Default = `False`.

