# coding=utf-8
arquivo = open('texto.txt', 'r', encoding='utf-8')   # Abre o arquivo e define o encoding para utf-8 (acentuação)

texto = arquivo.readlines()


#  percorre cada linha do texto
for linha in texto:
    print(linha)

# fecha a conexão/utilização do arquivo
arquivo.close()
