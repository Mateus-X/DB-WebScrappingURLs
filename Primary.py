import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor
import tldextract
import regex as re
import urllib3

def dedomain(info):
    extraction = tldextract.extract(info)
    domain = "{}.{}".format(extraction.domain, extraction.suffix)

    if extraction.subdomain.startswith("www"):
        procedure = "https://" if info.startswith("https://") else "http://"
        return procedure + "www." + domain
    else:
        procedure = "https://" if info.startswith("https://") else "http://"
        return procedure + domain

def ler_arq(nomearq):
    with open(nomearq, 'r+') as arq:
        info = arq.readlines()
    return [n.strip() for n in info]

def extraction(pag):
    simulation = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                  'Accept': '*/*'}
    pattern = re.compile(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b')
    try:
        req = requests.get(pag, headers=simulation, timeout=30, verify=False)
        req.raise_for_status()
        soup = BeautifulSoup(req.text, 'html.parser')
        urls = [tag.get('href') for tag in soup.find_all('a') if tag.get('href')]
        insta = [tag.get('href') for tag in soup.find_all('a') if tag.get('href') and 'instagram' in tag.get('href')]
        cnpjs = re.findall(pattern, req.text)
        return urls, cnpjs, insta, None
    except requests.RequestException as e:
        return [], [], [], str(e)

def process_url(index_url):
    index, url = index_url
    conn = sqlite3.connect('nova.db')
    cursor = conn.cursor()
    print(f"Processando URL {index + 1}/{total_urls}: {url}")

    processed_urls = set()
    found_instagrams = set()
    found_cnpjs = set()

    def extract_and_process(current_url):
        if current_url in processed_urls:
            return
        processed_urls.add(current_url)

        print(current_url)

        urls, cnpjs, insta, erro = extraction(current_url)
        datahora = datetime.now().isoformat(sep=' ')

        if erro:
            cursor.execute('INSERT INTO testes (site_origem, erro, url, instagram, cnpj, data_hora) VALUES (?, ?, ?, ?, ?)',
                           (url, True, current_url, None, None, datahora))
        else:
            if not insta and not cnpjs:
                cursor.execute('INSERT INTO testes (site_origem, erro, url, instagram, cnpj, data_hora) VALUES (?, ?, ?, ?, ?)',
                                   (url, False, current_url, None, None, datahora))
            else:
                for link in insta:
                    if link not in found_instagrams:
                        found_instagrams.add(link)
                        cursor.execute('INSERT INTO testes (site_origem, erro, url, instagram, cnpj, data_hora) VALUES (?, ?, ?, ?, ?)',
                                   (url, False, current_url, link, None, datahora))
            
            for cnpj in cnpjs:
                if cnpj not in found_cnpjs:
                    found_cnpjs.add(cnpj)
                    cursor.execute('INSERT INTO testes (site_origem, erro, url, instagram, cnpj, data_hora) VALUES (?, ?, ?, ?, ?)',
                                   (url, False, current_url, None, cnpj, datahora))
            
            for link in urls:
                extract_and_process(link)

    extract_and_process(url)
    conn.commit()
    conn.close()

# Main code
if __name__ == "__main__":
    conex = sqlite3.connect('nova.db')
    cursor = conex.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS testes (site_origem Text, erro BOOLEAN, url Text, instagram Text, cnpj Text, data_hora datetime)")
    conex.commit()
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    origins = ler_arq("testebasicsites.csv")
    origins = [dedomain(conts) for conts in origins]

    total_urls = len(origins)

    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.map(process_url, enumerate(origins))

    conex.commit()
    conex.close()
