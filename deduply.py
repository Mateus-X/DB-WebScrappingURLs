def deduplicar_arquivo():

    nome_arquivo = input('Digite o nome do arquivo que deseja deduplicar:')
    nome_novo_arquivo = input('Digite o nome do arquivo deduplicado:')
    
    # Passo 1: Ler o conteúdo do arquivo
    with open(nome_arquivo, 'r') as arquivo:
        linhas = arquivo.readlines()

    # Passo 2: Remover duplicatas usando um conjunto
    linhas_unicas = list(set(linhas))

    # Passo 3: Escrever o conteúdo sem duplicatas de volta no arquivo
    with open(nome_novo_arquivo, 'w') as arquivo:
        arquivo.writelines(linhas_unicas)

# Chamar a função com o nome do arquivo
deduplicar_arquivo()
