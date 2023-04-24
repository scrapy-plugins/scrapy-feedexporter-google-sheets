# GoogleSheets Exporter for Scrapy
[Scrapy feed export storage backend](https://doc.scrapy.org/en/latest/topics/feed-exports.html#storage-backends) for GoogleSheets.

## Requirements
-  Python 3.8+

## Installation
```bash
pip install git+https://github.com/scrapy-plugins/scrapy-feedexporter-google-sheets
```

## Usage
* Add this storage backend to the [FEED_STORAGES](https://docs.scrapy.org/en/latest/topics/feed-exports.html#std-setting-FEED_STORAGES) Scrapy setting. For example:
    ```python
    # settings.py
    FEED_STORAGES = {'gsheets': 'scrapy_google_sheets_exporter.gsheets_exporter.GoogleSheetsFeedStorage'}
    ```
* Configure [authentication](https://developers.google.com/identity/protocols/oauth2/service-account) with GOOGLE service account credentials like following:
  
  For example,
  ```python
  GOOGLE_CREDENTIALS = { 
        "type": "service_account", 
        "project_id": "project_id here", 
        "private_key_id": "private_key_id here", 
        "private_key": "private_key here", 
        "client_email": "client_email here", 
        "client_id": "client_id here", 
        "auth_uri": "auth_uri here", 
        "token_uri": "token_uri here", 
        "auth_provider_x509_cert_url": "auth_provider_x509_cert_url here", 
        "client_x509_cert_url": "client_x509_cert_url here" 
  }
    ```
* Give access of the folder (where you want to export the file) to the service account used in previous step. This can be done by sharing that folder with the service account's email (available in credentials as `client_email`)
* Configure in the [FEEDS](https://docs.scrapy.org/en/latest/topics/feed-exports.html#feeds) Scrapy setting the Google Drive URI where the feed needs to be exported.

    ```python
    FEEDS = {
        "gsheets://<spreadsheet_key>/<worksheet_name>": {
            "format": "csv",
            "append_mode": False
        }
    }
    ```
  - You can get the `spreadsheet_key` of the googlesheet.
    - e.g: `https://drive.google.com/drive/folders/<folder id is here>`
    
## Feed Options
- For now, this feed exporter only supports `csv` format. 
- The `append_mode` [feed option](https://docs.scrapy.org/en/latest/topics/feed-exports.html#feed-options) 

