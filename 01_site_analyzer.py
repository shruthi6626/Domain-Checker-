import csv
import json
import ssl
import socket
import re
import os
import time
from transformers import AutoTokenizer
import whois 
from datetime import datetime
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import pandas as pd
import argparse
from config import *

def remove_schema(url):
    pattern = re.compile(r'^(?:http|https):\/\/(?:www\.)?', re.IGNORECASE)
    cleaned_url = re.sub(pattern, '', url)    
    return cleaned_url

def write_to_file(data, filename):
    with open(filename, 'a') as file:
        for item in data:
            file.write(item + '\n')

def replace_multiple_spaces_with_one(text):
    return re.sub(r'\s+', ' ', text).strip()

def remove_non_ascii(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

def truncate_text(text, max_length, tokenizer):
    tokens = tokenizer.encode(text)
    if len(tokens) > max_length:
        return tokenizer.decode(tokens[:max_length], skip_special_tokens=True, clean_up_tokenization_spaces=True)
    return text

def get_source_selenium(url, driver, source_path):
    try:
        if 'https://' not in url:
            url = 'https://' + url
        filename = url.replace('https://', '').replace('http://', '').replace('/', '').replace('?', '').replace('!', '').replace('@', '').replace(':', '') + '.html'
        fpath = os.path.join(source_path, filename)
        if os.path.exists(fpath):
            with open(fpath, 'r') as file:
                content = file.read()
            return content
        else:
            print(f"file does not exist: {url}")
            driver.get(url)
            time.sleep(6)
            content = driver.page_source
            with open(fpath, 'w') as fout:
                fout.write(content)
            return content
    except Exception as e:
        print(f'Error for {url} because: {e}')


def extract_body_text(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    body_text = soup.body.get_text(separator=' ', strip=True) if soup.body else ''
    return body_text

def extract_whois_info(record_dict):
    extracted_info = ''
    text = record_dict['text']
    registrar_match = re.search(r'Registrar: (.*)\r\n', text)
    expiry_match = re.search(r'Registry Expiry Date: (.*)\r\n', text)
    registrar = registrar_match.group(1).strip() if registrar_match else "Not found"
    expiry_date = expiry_match.group(1).strip() if expiry_match else "Not found"
    extracted_info += 'registrarName:' + registrar + ' expiresDate:' + expiry_date
    return extracted_info

def extract_ssl_info(certificate_info):
    try:
        if type(certificate_info) == str:
            print(f"{certificate_info}")
        not_before_date = datetime.strptime(certificate_info['notBefore'], '%b  %d %H:%M:%S %Y %Z')
        not_after_date = datetime.strptime(certificate_info['notAfter'], '%b  %d %H:%M:%S %Y %Z')

        issuer_info = certificate_info['issuer']
        issuer_common_name = ''
        for key_value in issuer_info:
            if key_value[0][0] == 'commonName':
                issuer_common_name = key_value[0][1]
                break
        cert_valid_period = (not_after_date - not_before_date).days
        current_date = datetime.now()
        cert_age = (current_date - not_before_date).days
        extracted_info = "certIssuer:" + issuer_common_name + " certValidPeriod:" + str(cert_valid_period) + " certAge:" + str(cert_age)
        return extracted_info
        
    except Exception as e:
        print(f'Failed to parse SSL dict for because: {e}')
        return ""

def fetch_whois_info(domain):
    try:
        domain_info = whois.whois(domain)
        result_dict = {}
        for attribute in dir(domain_info):
            if not attribute.startswith("_") and not callable(getattr(domain_info, attribute)):
                value = getattr(domain_info, attribute)
                result_dict[attribute] = value
        return result_dict
    except Exception as e:
        print(f"Error fetching WHOIS info for {domain} because: {e}")

def extract_external_links(source, domain):
    soup = BeautifulSoup(source, 'html.parser')
    a_tags = soup.find_all('a')
    domain_no_tld = domain.split('.')[0]
    outgoing_links = []
    for tag in a_tags:
        href = tag.get('href')
        if href:
            parsed_href = urlparse(href)
            href_netloc = parsed_href.netloc
            if bool(href_netloc) and domain_no_tld not in href_netloc and not href.startswith("/"):
                outgoing_links.append(href)

    formatted_string = ", ".join(f"'{url}'" for url in outgoing_links)
    return formatted_string

def extract_domain(url):
    if not urlparse(url).scheme:
        url = 'http://' + url
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain

def get_urls_from_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        if 'URL' not in df.columns:
            raise ValueError("CSV file does not contain a 'URL' column")
        urls = df['URL'].tolist()
        return urls
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except pd.errors.EmptyDataError:
        print(f"Error: '{file_path}' is empty.")
    except pd.errors.ParserError as e:
        print(f"Error parsing CSV file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return []

def process_domains(url, source_path, jsonl_output):
    print("------")
    driver = None
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8b")
    try:
        print(f"sel add : {selenium_address}")
        d = DesiredCapabilities.CHROME
        d['goog:loggingPrefs'] = { 'performance':'ALL', 'browser':'ALL' }
        options = Options()
        options.add_argument("--incognito")
        options.add_argument("--enable-javascript")
        options.add_argument("--ignore-certificate-errors")
        driver = webdriver.Remote(selenium_address, d, options=options)
        driver.set_page_load_timeout(15)
        print('DRIVER LOADED')
        with open(jsonl_output, 'w', encoding='utf-8') as jsonlfile:
            if url:
                try:
                    
                    domain = remove_schema(extract_domain(url))
                    all_content = get_source_selenium(domain, driver, source_path)
                    if all_content != None:
                        body_text = extract_body_text(all_content)
                        content = remove_non_ascii(body_text).replace('\n', ' ')
                        _content = replace_multiple_spaces_with_one(content)
                        
                        if not content or len(_content) < 200 or (_content != None and 'HTTP Error 403' in _content):
                            print(f"error for url {url} is : HTTP Error 403")
                            return

                        whois_info_all = fetch_whois_info(domain)
                        whois_info = ''
                        if whois_info_all:
                            whois_info = extract_whois_info(whois_info_all)

                        external_links = extract_external_links(all_content, domain)
                        dynamic_content = f"# URL:\n{domain}\n\n# External Links:\n{external_links}\n\n# WHOIS Information:\n{whois_info}\n\n"
                        dynamic_tokens_len = len(tokenizer.encode(dynamic_content))
                        reserved_tokens_for_non_body_text = len(tokenizer.encode('# URL:\n\n\n# Website Content:\n\n\n')) + dynamic_tokens_len + len(tokenizer.encode("scam"))
                        max_length_for_body_text = 8000 - reserved_tokens_for_non_body_text
                        if max_length_for_body_text < 0:
                            print(reserved_tokens_for_non_body_text )
                        truncated_content = truncate_text(_content, max_length_for_body_text, tokenizer)
                        prompt = f"# URL:\n{domain}\n\n# Website Content:\n{truncated_content}\n\n# External Links:\n{external_links}\n\n# WHOIS Information:\n{whois_info}\n\n# Pred:\n"
                        tmp = {'input': prompt}
                        jsonlfile.write(json.dumps(tmp) + '\n')
                        jsonlfile.flush()
                except Exception as e:
                    print(f"error for url {url} is : {e}")

    except Exception as e:
        print('Potential issue with driver', e)
        try:
            driver.quit()
        except Exception as e:
            print('Error while quiting driver', e)        

def extract_whois_info_jsonl(record_dict, fields):
    extracted_info = ''
    if 'records' in record_dict and record_dict['records'] is not None and len(record_dict['records']) > 0:
        record = record_dict['records'][0]
        for field in fields:
            if field in record:
                extracted_info += field + ':' + record[field] + ' '
    
    return extracted_info



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process domain(s) and generate domain info.")
    parser.add_argument('-u', '--input-url', required=False, help='input url')
    parser.add_argument('-s', '--saved_pages', required=True, help='Directory containing saved pages')
    parser.add_argument('-o', '--output', required=True, help='Path to the output JSONL file')

    args = parser.parse_args()

    process_domains(args.input_url, args.saved_pages, args.output)
