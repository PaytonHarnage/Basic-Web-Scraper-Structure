import requests
from bs4 import BeautifulSoup
import re
import ssl
import socket


# Function to fetch the page content
def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if request was successful
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None


# Function to parse the HTML content
def parse_page(page_content):
    soup = BeautifulSoup(page_content, 'lxml')
    return soup


# Function to find exposed email addresses
def find_emails(soup):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, str(soup))
    return set(emails)  # Return unique emails


# Function to fetch the robots.txt file
def fetch_robots_txt(url):
    robots_url = url + "/robots.txt"
    page_content = fetch_page(robots_url)
    if page_content:
        return page_content
    return None


# Function to check for sensitive directories in robots.txt
def check_robots_for_sensitive_dirs(robots_content):
    sensitive_dirs = ['backup', 'admin', 'private']
    for dir in sensitive_dirs:
        if dir in robots_content:
            print(f"Warning: Potential exposed directory found: {dir}")


# Function to check if the website uses HTTPS
def check_https(url):
    domain = url.replace('https://', '').replace('http://', '')
    context = ssl.create_default_context()
    try:
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                print(f"{url} uses HTTPS.")
    except Exception as e:
        print(f"{url} does not use HTTPS or is insecure: {e}")


# Function to get internal links from the page
def get_internal_links(soup, base_url):
    links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith(base_url):  # Ensure it's an internal link
            links.add(href)
    return links


# Main function to run the scraper
def main():
    url = input("Enter the URL to analyze (e.g., https://example.com): ")

    # Fetch page content
    page_content = fetch_page(url)
    if page_content:
        soup = parse_page(page_content)

        # Find and display emails
        emails = find_emails(soup)
        if emails:
            print(f"\nFound emails: {emails}")
        else:
            print("\nNo emails found.")

        # Check for HTTPS usage
        check_https(url)

        # Check robots.txt for sensitive directories
        robots_content = fetch_robots_txt(url)
        if robots_content:
            check_robots_for_sensitive_dirs(robots_content)

        # Crawl internal links on the page
        print("\nCrawling internal links...")
        links = get_internal_links(soup, url)
        if links:
            print(f"Found internal links: {links}")
        else:
            print("No internal links found.")

if __name__ == "__main__":
    main()
    
