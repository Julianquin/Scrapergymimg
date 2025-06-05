import os
import re
import urllib.request
from html.parser import HTMLParser

BASE_URL = "https://darebee.com"
START_PAGE_TEMPLATE = BASE_URL + "/workout.html?start={start}"
START_STEP = 15
MAX_START = 2505


class LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr, value in attrs:
                if attr == "href":
                    self.links.append(value)


def fetch(url):
    """Fetches a URL and returns its HTML content."""
    print(f"Fetching {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        return response.read().decode("utf-8", errors="ignore")


def extract_links(html):
    parser = LinkExtractor()
    parser.feed(html)
    return parser.links


def get_workout_pages(start_index):
    url = START_PAGE_TEMPLATE.format(start=start_index)
    html = fetch(url)
    links = extract_links(html)
    # Workout pages follow /workouts/*-workout.html pattern
    workout_links = [
        BASE_URL + link for link in links if re.match(r"/workouts/.+\.html$", link)
    ]
    return workout_links


def get_pdf_link(workout_url):
    html = fetch(workout_url)
    links = extract_links(html)
    for link in links:
        if link.endswith(".pdf") and "/pdf/workouts/" in link:
            if not link.startswith("http"):
                link = BASE_URL + link
            return link
    return None


def download_file(url, dest_dir):
    filename = url.split("/")[-1]
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, filename)
    print(f"Downloading {url} -> {dest_path}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response, open(dest_path, "wb") as f:
        f.write(response.read())
    return dest_path


def scrape_all(dest_dir="pdfs"):
    pdf_urls = []
    for start in range(0, MAX_START + START_STEP, START_STEP):
        workout_pages = get_workout_pages(start)
        for page_url in workout_pages:
            pdf_url = get_pdf_link(page_url)
            if pdf_url:
                pdf_urls.append(pdf_url)
                download_file(pdf_url, dest_dir)
    return pdf_urls


if __name__ == "__main__":
    scrape_all()
