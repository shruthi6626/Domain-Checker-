import os
from bs4 import BeautifulSoup
from website_types import (
    is_shopping_page,
    is_blog_page,
    is_entertainment_page,
    is_education_page,
    is_gov_page,
    is_nonprofit_page,
)

def classify_website(html_file_path):
    with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ', strip=True).lower()

    if is_shopping_page(text):
        return "Shopping"
    elif is_blog_page(text):
        return "Blog"
    elif is_entertainment_page(text):
        return "Entertainment"
    elif is_education_page(text):
        return "Education"
    elif is_gov_page(text):
        return "Government"
    elif is_nonprofit_page(text):
        return "Nonprofit"
    else:
        return "Unknown"

if __name__ == "__main__":
    saved_dir = "./saved_pages"
    print(f"Looking for HTML files in: {saved_dir}")
    try:
        files = os.listdir(saved_dir)
    except FileNotFoundError:
        print(f"Folder {saved_dir} does not exist!")
        exit(1)

    print(f"Found files: {files}")

    found_any = False
    for filename in files:
        if filename.endswith(".html"):
            found_any = True
            path = os.path.join(saved_dir, filename)
            site_type = classify_website(path)
            print(f"{filename}: {site_type}")

    if not found_any:
        print("No HTML files found in the directory.")

    print("Done processing files.")
