import os
from bs4 import BeautifulSoup

saved_pages_dir = 'saved_pages'
output_dir = 'cleaned_texts'

os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(saved_pages_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(saved_pages_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            html = file.read()

        soup = BeautifulSoup(html, 'html.parser')

        for tag in soup(['script', 'style', 'noscript', 'iframe', 'meta', 'link']):
            tag.decompose()

        visible_text = soup.get_text(separator=' ', strip=True)

        output_path = os.path.join(output_dir, filename.replace('.html', '.txt'))

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(visible_text)

        print(f"✅ Cleaned text saved to: {output_path}")
