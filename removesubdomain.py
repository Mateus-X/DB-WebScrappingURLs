import tldextract

def ler_arq(nomearq):
    with open(nomearq, 'r+') as arq:
        info = arq.readlines()
    return [n.strip() for n in info]

def escrever_arq(nomearq2, conteudo):
    with open(nomearq2, 'a') as arq:
        arq.write(conteudo + '\n')


def dedomain(info):
    extraction = tldextract.extract(info)
    domain = "{}.{}".format(extraction.domain, extraction.suffix)

    if extraction.subdomain.startswith("www"):
        procedure = "https://" if info.startswith("https://") else "http://"
        return procedure + "www." + domain
    else:
        procedure = "https://" if info.startswith("https://") else "http://"
        return procedure + domain
    


if __name__ == '__main__':
    content = ler_arq('sites.txt')

    wthsbd = [dedomain(conts) for conts in content]

    for what in wthsbd:
        escrever_arq('siteswthsbd/.csv', what)
    
    




