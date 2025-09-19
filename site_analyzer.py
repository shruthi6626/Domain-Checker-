import argparse
import json
import os
from bs4 import BeautifulSoup
import requests
import whois
from urllib.parse import urljoin, urlparse

def extract_visible_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text(separator=' ', strip=True)

def extract_external_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc != urlparse(base_url).netloc:
            links.add(full_url)
    return list(links)

def get_whois_info(domain):
    try:
        w = whois.whois(domain)
        registrar = w.registrar or "Unknown"
        expires = str(w.expiration_date) if w.expiration_date else "Unknown"
        return f"registrarName:{registrar} expiresDate:{expires}"
    except:
        return "registrarName:Unknown expiresDate:Unknown"

def process_domain(domain):
    url = f"http://{domain}"
    try:
        response = requests.get(url, timeout=10)
        html = response.text
        text = extract_visible_text(html)[:300]
        links = extract_external_links(html, url)
        whois_info = get_whois_info(domain)
        prompt = f"# URL:\n{domain}\n\n# Website Content:\n{text}\n\n# External Links:\n{links}\n\n# WHOIS Information:\n{whois_info}\n\n# Pred:\n"
        return {"input": prompt}
    except Exception as e:
        return {"input": f"# URL:\n{domain}\n\n# Website Content:\nError: {e}\n\n# External Links:\n[]\n\n# WHOIS Information:\nregistrarName:Unknown expiresDate:Unknown\n\n# Pred:\n"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-url', required=True)
    parser.add_argument('--saved_pages', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    os.makedirs(args.saved_pages, exist_ok=True)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    domain = args.input_url
    result = process_domain(domain)

    # Save HTML
    html_path = os.path.join(args.saved_pages, f"{domain}.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(requests.get(f"http://{domain}").text)

    # Save JSONL
    with open(args.output, 'a', encoding='utf-8') as out:
        out.write(json.dumps(result) + '\n')

if __name__ == "__main__":
    main()
