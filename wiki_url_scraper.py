import requests
from bs4 import BeautifulSoup
import csv
import urllib.parse
import sys
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Input CSV file with URLs
input_file = os.getenv("INPUT_FILE")

# Check if an argument for the output filename is provided
if len(sys.argv) < 2:
    print("Usage: python3 wiki_url_scraper.py <output_prefix>")
    sys.exit(1)

output_dir = 'output'
error_dir = 'logs'

# Get the output prefix from the command-line argument
output_prefix = sys.argv[1]

# Generate timestamps for filenames
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

# Output text file to save scraped URLs
output_txt = os.path.join(output_dir, f'{output_prefix}_{timestamp}.txt')

# Output text file to save URLs with errors
error_txt = os.path.join(error_dir, f'{output_prefix}_{timestamp}_errors.txt')

# Output CSV file
output_csv = os.path.join(error_dir, f'{output_prefix}_{timestamp}_log.csv')

# Initialize a list to store rows for the CSV file
csv_rows = []

# Initialize a list to store scraped URLs
scraped_urls = []

# Initialize counters
success_count = 0
error_count = 0

# Initialize a list to store URLs with errors
error_urls = []

# Read the CSV file and scrape each URL
with open(input_file, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='\t')
    for row in csv_reader:
        # Remove leading/trailing whitespace
        raw_url = row[0].strip()
        # Encode the URL to handle special characters
        #url = urllib.parse.quote(raw_url, safe='/:')
        url = raw_url

        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Initialize a variable to store the URL
            official_site_url = None

            # Find all <a> tags within "official-website" and "url" spans
            official_website_spans = soup.find_all('span', class_='official-website')
            url_spans = soup.find_all('span', class_='url')

            # Combine the lists of spans
            all_spans = official_website_spans + url_spans

            # Iterate through the spans to find the official site URL
            for span in all_spans:
                link = span.find('a', href=True)
                if link:
                    official_site_url = link['href']
                    break

            # Append the scraped URL to the list
            scraped_urls.append(official_site_url)

            # Append the data for the CSV file
            csv_rows.append([raw_url, url, official_site_url])

            # Print progress message and increment success_count
            print("Scraped webpage:", url)
            success_count += 1

            if official_site_url:
                print("Official Site URL:", official_site_url)
            else:
                # Print error message and increment error_count
                print("Official Site URL not found on", url)
                error_count += 1
                error_urls.append(url)
        else:
            # Print error message and increment error_count
            print(f"Failed to retrieve the webpage {url}. Status code:", response.status_code)
            error_count += 1
            error_urls.append(url)

# Output CSV file
with open(output_csv, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    # Write header row
    csv_writer.writerow(['Input URL', 'Requested URL', 'Scraped URL'])
    # Write the rows collected during scraping
    csv_writer.writerows(csv_rows)

# Save the scraped URLs to the output text file
with open(output_txt, 'w') as txt_file:
    for url in scraped_urls:
        if url:
            txt_file.write(url + '\n')

# Save URLs with errors to a separate text file
with open(error_txt, 'w') as error_file:
    for url in error_urls:
        error_file.write(url + '\n')

# Count the number of lines in the output text file
with open(output_txt, 'r') as txt_file:
    line_count = sum(1 for line in txt_file)

print("------------------")
print("Scraping completed. URLs saved to", output_txt)
print("URLs with errors saved to", error_txt)
print("------------------")
# Print summary
print("Total URLs scraped:", success_count)
print("Total URLs with errors:", error_count)
print("Total lines in output file:", line_count)