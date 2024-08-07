import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup
import requests

conex = sqlite3.connect('DB-WS.db')
cursor = conex.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS sites (site_origem Text, url Text, data_hora datetime)")
conex.commit()


def ler_arq(nomearq):
    with open(nomearq, 'r+') as arq:
        info = arq.readlines()
    return info


origins = ler_arq("testesites.txt") #Aux = Sites_Origem (LIST)
orig = [n.strip() for n in origins]

def extraction(pag):
    try:
        req = requests.get(pag)
        req.raise_for_status()
        content = req.text

        soup = BeautifulSoup(content, 'html.parser')
        urls = [tag.get('href') for tag in soup.find_all('a') if tag.get('href')]
        return urls, None
    except requests.RequestException as e:
        return [], str(e)


#delete from testes
for url in orig:
    pags, erro = extraction(url) #Pag = Hiperlinks

    if erro:
        cursor.execute('INSERT INTO sites (site_origem, url, data_hora) VALUES (?, ?, ?)', (url, erro, None))
    else:
        for links in pags:
            datahora = datetime.now().isoformat(sep=' ')
            cursor.execute('INSERT INTO sites (site_origem, url, data_hora) values (?, ?, ?)', (url, links, datahora))

conex.commit()

conex.close()   