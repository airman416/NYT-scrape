# Web Scraper for News Articles

## Prerequisites

Install the required Python packages:

```bash
pip install pandas mechanize beautifulsoup4 certifi
```

And download the source data (currently only NYT) from [here](https://northeastern-my.sharepoint.com/:f:/g/personal/agrawal_arm_northeastern_edu/EvjxrJI8UIJPtGwNvpjAnj0BkqOhKAK7MgdNIchTr7NIaw?e=mlAvSn).

## Input CSV Format

Your input CSV file should contain at least these columns:
- `url`: The URL of the article to scrape
- `sentiment`: A sentiment score for the article
- `date` (optional): The date of the article
- `headline` (optional): The article headline (will be scraped if not provided)

## Usage

### Process a Single CSV File

```bash
python bsoup.py path/to/input.csv
```

### Process a Limited Number of Rows

```bash
python bsoup.py path/to/input.csv --nrows 10
```

### Process All CSV Files in a Directory

```bash
python bsoup.py path/to/directory --all
```

## Output

The script creates an `output` directory containing the processed files. For each input CSV file named `input.csv`, it creates a corresponding `input_out.csv` file with the following columns:

- `date`: Article date (if provided in input)
- `url`: Original article URL
- `sentiment_score`: Sentiment score from input
- `full_headline`: Article headline (scraped or from input)
- `article_text`: Full article content
- `author`: Article author (or "Unknown" if not found)

## Notes

- The script will skip URLs that return errors
- Processing continues even if individual files fail
- Detailed error messages are displayed for troubleshooting
- The script includes random delays between requests to avoid being blocked
- SSL certificate verification is disabled for compatibility
- User-Agent headers are set to mimic a web browser
