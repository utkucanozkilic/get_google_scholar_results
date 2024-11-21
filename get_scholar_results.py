import requests
from bs4 import BeautifulSoup
import csv
import time


def fetch_scholar_results(query, start = 0, retries = 5):
    """Fetch Google Scholar search results with retry mechanism."""
    base_url = "https://scholar.google.com/scholar"
    params = {
        "start": start,
        "q": query,
        "hl": "tr",
        "as_sdt": "0,5"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    for attempt in range(retries):
        response = requests.get(base_url, params = params, headers = headers)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 429:
            wait_time = (attempt + 1) * 10
            print(f"Too many requests. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            print(f"Unexpected error: {response.status_code}")
            time.sleep(5)
    raise Exception("Failed to fetch results after multiple attempts.")


def parse_results(html):
    """Parse the search results and extract article URLs."""
    soup = BeautifulSoup(html, "html.parser")
    articles = []
    for result in soup.select(".gs_r.gs_or.gs_scl"):
        link_tag = result.select_one(".gs_rt a")
        if link_tag and link_tag.get("href"):
            articles.append(link_tag["href"])
    return articles


def fetch_article_details(url):
    """Fetch title and abstract from the given URL."""
    try:
        response = requests.get(url, headers = {"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return None, None
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract the title
        title = soup.title.string if soup.title else "Title not found"

        # Extract the abstract
        abstract = soup.find("meta", {"name": "description"})
        if abstract and abstract.get("content"):
            abstract = abstract["content"]
        else:
            abstract = "Abstract not found"

        return title, abstract
    except Exception as e:
        print(f"Error fetching details from {url}: {e}")
        return None, None


def save_to_csv(data, filename = "scholar_results_with_details.csv"):
    """Save a list of URLs and their details to a CSV file."""
    with open(filename, mode = "w", newline = "", encoding = "utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Article URL", "Title", "Abstract"])
        writer.writerows(data)


def scrape_google_scholar(query, max_results = 50, step = 10):
    """Scrape Google Scholar results and fetch details from each link."""
    all_results = []
    for start in range(0, max_results, step):
        print(f"Fetching results {start + 1}-{start + step}...")
        html = fetch_scholar_results(query, start=start)
        urls = parse_results(html)
        for url in urls:
            print(f"Fetching details for: {url}")
            title, abstract = fetch_article_details(url)
            all_results.append([url, title, abstract])
            time.sleep(2)  # Increase delay to avoid rate limits
    return all_results


# Query
query = ("(Refuge* OR Migrant* OR Immigrant* OR asylum OR asylee OR newcomer OR immigration) AND (youth* OR juvenile OR"
         " adolescen* OR child OR teen*) AND (delinquency* OR crim* OR offend* OR devian*) -site:books.google.com")

# Scrape Google Scholar
max_results = 50  # Fetch first 50 results
results = scrape_google_scholar(query, max_results = max_results)

# Save results to CSV
save_to_csv(results, filename = "scholar_results_with_details.csv")

print(f"Total {len(results)} articles with details saved to scholar_results_with_details.csv.")
