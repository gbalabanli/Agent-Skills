# Unsplash API Notes

Use this file as the minimal reference for the bundled downloader script.

## Required Auth

- Header: `Authorization: Client-ID <UNSPLASH_ACCESS_KEY>`
- Header: `Accept-Version: v1`
- The script reads the key from `UNSPLASH_ACCESS_KEY` or `--access-key`.

## Search Endpoint

- Method: `GET`
- URL: `https://api.unsplash.com/search/photos`
- Required query parameter: `query`
- Useful optional params:
  - `page`
  - `per_page` (max 30 for this skill script)
  - `orientation` (`landscape`, `portrait`, `squarish`)
  - `content_filter` (`low`, `high`)

## Download Tracking Endpoint

- Use `links.download_location` from the selected photo object.
- Call the URL with the same auth headers.
- Use the returned `url` field to download the binary image.

## Primary Docs

- https://unsplash.com/documentation
