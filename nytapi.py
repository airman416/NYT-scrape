import csv
import requests
from pynytimes import NYTAPI
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
# Initialize the NY Times API client
api_key = os.getenv('NYTIMES_API_KEY')
nyt = NYTAPI(api_key, parse_dates=True)

# Function to get article details using the Article Search API
def get_article_details(url):
    api_url = f"https://api.nytimes.com/svc/search/v2/articlesearch.json?fq=web_url:(\"{url}\")&api-key={api_key}"
    response = requests.get(api_url)
    print(api_url)
    if response.status_code == 200:
        data = response.json()
        if 'response' in data and 'docs' in data['response'] and len(data['response']['docs']) > 0:
            article = data['response']['docs'][0]
            return {
                'abstract': article.get('abstract', ''),
                'lead_paragraph': article.get('lead_paragraph', ''),
                'pub_date': article.get('pub_date', ''),
                'source': article.get('source', '')
            }
    return None

# Read the input CSV file
input_file = ("/Users/armaanagrawal/Downloads/headlinesDataWithSentiment"
              "LabelsAnnotationsFromSentimentRobertaLargeModel/nyt/2000.csv")
output_file = 'output.csv'

df = pd.read_csv(input_file, nrows=10)

with open(input_file, 'r') as csvfile, open(output_file, 'w', newline='') as outfile:
    reader = csv.DictReader(csvfile)
    fieldnames = ['sentiment', 'headline', 'url', 'abstract', 'lead_paragraph', 'pub_date', 'source']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for _, row in df.iterrows():
        sentiment = row['sentiment']
        headline = row['headline']
        url = row['url']

        # Get additional article details
        article_details = get_article_details(url)

        if article_details:
            writer.writerow({
                'sentiment': sentiment,
                'headline': headline,
                'url': url,
                'abstract': article_details['abstract'],
                'lead_paragraph': article_details['lead_paragraph'],
                'pub_date': article_details['pub_date'],
                'source': article_details['source']
            })
        else:
            writer.writerow({
                'sentiment': sentiment,
                'headline': headline,
                'url': url,
                'abstract': '',
                'lead_paragraph': '',
                'pub_date': '',
                'source': ''
            })

print("Scraping completed. Results saved to output.csv")
