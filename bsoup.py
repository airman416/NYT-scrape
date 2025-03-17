import csv
import pandas as pd
import mechanize
from bs4 import BeautifulSoup
import http.cookiejar
import time
import random
import ssl
import certifi
from urllib.error import HTTPError, URLError
import argparse
import os


def setup_browser():
    browser = mechanize.Browser()

    cj = http.cookiejar.LWPCookieJar()
    browser.set_cookiejar(cj)

    browser.set_handle_equiv(True)
    browser.set_handle_redirect(True)
    browser.set_handle_referer(True)
    browser.set_handle_robots(False)  # Ignore robots.txt

    browser.addheaders = [('User-agent',
                           'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')]

    # SSL context
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE  # Disable certificate verification
    browser.set_ca_data(cafile=certifi.where())

    return browser


# Function to scrape article content
def scrape_article_content(url, browser):
    try:
        # Add random delay to avoid being blocked
        time.sleep(random.uniform(1, 3))

        response = browser.open(url, timeout=30.0)
        html_content = response.read()
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract headline
        headline = None
        headline_element = soup.find('h1', class_='e1h9rw200') or \
                         soup.find('h1', class_='headline') or \
                         soup.find('h1', {'data-testid': 'headline'}) or \
                         soup.find('meta', {'property': 'og:title'}) or \
                         soup.find('meta', {'name': 'title'})
        
        if headline_element:
            if headline_element.get('content'):  # For meta tags
                headline = headline_element['content']
            else:  # For h1 tags
                headline = headline_element.get_text().strip()

        # Extract author with more comprehensive selectors
        author = None
        author_element = soup.find('meta', {'name': 'author'}) or \
                        soup.find('span', class_='byline-author') or \
                        soup.find('a', class_='author-name') or \
                        soup.find('span', class_='byline') or \
                        soup.find('div', class_='byline') or \
                        soup.find('p', class_='byline-name')

        if author_element:
            if author_element.get('content'):  # For meta tags
                author = author_element['content']
            else:  # For span, div, or p tags
                author = author_element.get_text().strip()
                # Clean up common patterns in author text
                author = author.replace('By ', '').replace('by ', '').strip()

        # Extract article content
        article_body = soup.find('section', {'name': 'articleBody'}) or \
                      soup.find('div', class_='StoryBodyCompanionColumn') or \
                      soup.find('div', id='articleBody') or \
                      soup.find('div', class_='article-body')

        if article_body:
            paragraphs = article_body.find_all('p')
            content = ' '.join([p.get_text().strip() for p in paragraphs])
            return content, headline, author
        else:
            # Try alternative selectors if the main ones don't work
            paragraphs = soup.select('article p') or \
                        soup.select('.article-content p') or \
                        soup.select('#story p') or \
                        soup.select('.story-body p')

            if paragraphs:
                content = ' '.join([p.get_text().strip() for p in paragraphs])
                return content, headline, author

            # Last resort: get all paragraphs from the page
            all_paragraphs = soup.find_all('p')
            if all_paragraphs:
                content = ' '.join([p.get_text().strip() for p in all_paragraphs])
                return content, headline, author

            return "Content not found", headline, author

    except (HTTPError, URLError) as e:
        return f"Error accessing URL: {str(e)}", None, None
    except Exception as e:
        return f"Error scraping content: {str(e)}", None, None


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Scrape NYT articles')
    parser.add_argument('input_file', help='Path to input CSV file')
    parser.add_argument('--nrows', type=int, help='Number of rows to process (optional)', default=None)
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    # Generate output filename by adding "_out.csv" to the input filename (without extension)
    input_filename = os.path.basename(args.input_file)  # Get just the filename without path
    base_name = os.path.splitext(input_filename)[0]
    output_file = os.path.join(output_dir, f"{base_name}_out.csv")

    try:
        # Read input file with optional nrows parameter
        df = pd.read_csv(args.input_file, nrows=args.nrows)
        browser = setup_browser()

        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ['date', 'url', 'sentiment_score', 'full_headline', 
                         'article_text', 'author']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for _, row in df.iterrows():
                sentiment = row['sentiment']
                url = row['url']
                date = row.get('date', '')

                print(f"Scraping URL: {url}")

                content, scraped_headline, author = scrape_article_content(url, browser)
                
                # Use scraped headline if available, otherwise fall back to the one from CSV
                headline = scraped_headline if scraped_headline else row.get('headline', '')

                writer.writerow({
                    'date': date,
                    'url': url,
                    'sentiment_score': sentiment,
                    'full_headline': headline,
                    'article_text': content,
                    'author': author or 'Unknown'
                })

                time.sleep(random.uniform(2, 5))

        print(f"Scraping completed. Results saved to {output_file}")

    except FileNotFoundError:
        print(f"The file '{args.input_file}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
