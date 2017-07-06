import socket
HOST = 'localhost'              # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

count = 0
arquivo = open('texto.txt', 'r', encoding='utf-8')
texto = arquivo.readlines()
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
orig = (HOST, PORT)
tcp.bind(orig)
tcp.listen(1)
while True:
    con, cliente = tcp.accept()
    print ('Concetado por', cliente)
    con.send(' '.join(texto).encode(encoding='UTF-8'))




con.close()