from firecrawl import FirecrawlApp
import json

from dotenv import load_dotenv
import os

load_dotenv()

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Scrape a website:
scrape_result = app.scrape_url('https://docs.boundaryml.com/docs', params={'formats': ['markdown', 'html']})

# Save content to txt file
with open('scrape_result.txt', 'w', encoding='utf-8') as f:
    json.dump(scrape_result, f, ensure_ascii=False, indent=4)

print("Scrape result saved to scrape_result.txt")
print(scrape_result)

map_result = app.map_url('https://docs.boundaryml.com/docs')
with open('map_resulats.txt', 'w', encoding='utf-8') as f:
    json.dump(map_result, f, ensure_ascii=False, indent=4)

links = map_result['links']

# print(links[0])
import os
from tqdm import tqdm

# Create a directory to store the crawled results
if not os.path.exists('crawled_results'):
    os.makedirs('crawled_results')

# Iterate through the links and crawl each one
for index, link in enumerate(tqdm(links, desc="Crawling links")):
    try:
        # Crawl the link
        crawl_result = app.scrape_url(link, params={'formats': ['markdown', 'html']})
        
        # Sleep for 10 seconds after scraping
        import time
        time.sleep(8)
        
        # Generate a filename based on the link
        filename = f"crawled_docs/result_{index}.json"
        
        # Save the crawl result to a file
        # Ensure the directory exists before writing the file
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(crawl_result, f, ensure_ascii=False, indent=4)
        
        print(f"Saved result for {link} to {filename}")
    except Exception as e:
        print(f"Error crawling {link}: {str(e)}")

print("Crawling completed. Results saved in 'crawled_results' directory.")
