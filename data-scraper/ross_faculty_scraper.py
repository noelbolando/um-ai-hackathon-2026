"""
Michigan Ross Faculty Directory Scraper
----------------------------------------
Scrapes faculty names, titles, and bio descriptions from:
https://michiganross.umich.edu/faculty-research/directory

Requirements:
    pip install requests beautifulsoup4

Usage:
    python scrape_ross_faculty.py
    
Output:
    ross_faculty.csv
"""

import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://michiganross.umich.edu"
DIRECTORY_URL = BASE_URL + "/faculty-research/directory"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def get_faculty_links_from_page(page_num):
    """Scrape faculty name, title(s), and profile URL from a directory page."""
    url = DIRECTORY_URL if page_num == 0 else f"{DIRECTORY_URL}?page={page_num}"
    print(f"  Fetching directory page {page_num + 1}: {url}")

    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code != 200:
        print(f"  WARNING: Got status {resp.status_code} for page {page_num + 1}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    articles = soup.select("article.faculty__teaser")

    faculty_list = []
    for article in articles:
        # Name
        name_tag = article.select_one(".grid__teaser__title a")
        name = name_tag.get_text(strip=True) if name_tag else "N/A"
        profile_path = name_tag["href"] if name_tag and name_tag.get("href") else ""
        profile_url = BASE_URL + profile_path if profile_path else ""

        # Titles (can be multiple)
        title_tags = article.select(".field--name-field-faculty-title .field__item")
        titles = " | ".join(t.get_text(strip=True) for t in title_tags)

        faculty_list.append({
            "name": name,
            "titles": titles,
            "profile_url": profile_url,
        })

    return faculty_list


def get_faculty_bio(profile_url):
    """Visit a faculty profile page and extract their bio description."""
    if not profile_url:
        return ""

    resp = requests.get(profile_url, headers=HEADERS, timeout=15)
    if resp.status_code != 200:
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")

    # Try common bio field selectors (adjust if needed)
    bio = ""

    # Try the main bio/about section
    for selector in [
        ".field--name-field-bio",
        ".field--name-body",
        ".faculty__bio",
        ".field--name-field-about",
        "[class*='bio']",
    ]:
        tag = soup.select_one(selector)
        if tag:
            bio = tag.get_text(separator=" ", strip=True)
            break

    # Fallback: look for paragraphs in the main content area
    if not bio:
        content = soup.select_one("main .node__content")
        if content:
            paragraphs = content.find_all("p")
            bio = " ".join(p.get_text(strip=True) for p in paragraphs[:5])

    return bio


def get_total_pages():
    """Check the first directory page to find how many pages exist."""
    resp = requests.get(DIRECTORY_URL, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    pager_items = soup.select(".pager__item a")
    page_nums = []
    for item in pager_items:
        href = item.get("href", "")
        if "page=" in href:
            try:
                num = int(href.split("page=")[1].split("&")[0])
                page_nums.append(num)
            except ValueError:
                pass
    return max(page_nums) + 1 if page_nums else 1  # 0-indexed, so +1


def main():
    print("=" * 55)
    print("Michigan Ross Faculty Scraper")
    print("=" * 55)

    # Step 1: Find total pages
    print("\nChecking number of directory pages...")
    total_pages = get_total_pages()
    print(f"Found {total_pages} pages of faculty listings.")

    # Step 2: Collect all faculty entries
    print("\nCollecting faculty names and titles...")
    all_faculty = []
    for page_num in range(total_pages):
        entries = get_faculty_links_from_page(page_num)
        all_faculty.extend(entries)
        time.sleep(1)  # Be polite — pause between requests

    print(f"\nFound {len(all_faculty)} faculty members total.")

    # Step 3: Visit each profile for bio
    print("\nFetching individual faculty bios (this may take a few minutes)...")
    for i, faculty in enumerate(all_faculty):
        print(f"  [{i+1}/{len(all_faculty)}] {faculty['name']}")
        faculty["bio"] = get_faculty_bio(faculty["profile_url"])
        time.sleep(0.75)  # Polite delay between profile requests

    # Step 4: Write to CSV
    output_file = "ross_faculty.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "titles", "bio", "profile_url"])
        writer.writeheader()
        writer.writerows(all_faculty)

    print(f"\nDone! Data saved to: {output_file}")
    print(f"Total faculty scraped: {len(all_faculty)}")


if __name__ == "__main__":
    main()
    