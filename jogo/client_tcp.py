# -*- coding: utf-8 -*-


from __future__ import print_function
import jogo.tic_tac_common as ttc

import socket
import sys
import os
import json, re, copy
import argparse

#Verifique o final do arquivo para configurar o ip e a porta do servidor

# ---------------------------------------------------------------------------- #


def main():

	s = ttc.get_client_socket()

	try:
		# Recebe mensagem de olá
		hello_msg = ttc.get_msg_from_socket(s)
		print("\n{0}\n".format(hello_msg))

		print('''
Você é a cruz/o xis (X).
Entre com as coordenadas, onde você deseja colocar o X.
Exemplo, canto do topo a esquerda será (0, 0).
No seguinte formato: <numero> <numero> <aperte Enter>
''')
		gf = copy.deepcopy(ttc.GAME_FIELD)
		ttc.print_game_field(gf)

		### Loop do jogo até ter um ganhador ou CTRL+C
		while True:


			#Pega a jogada do usuário
			turn_json = ttc.get_turn_from_user(gf)


			#Manda a jogada ao servidor
			s.sendall(turn_json.encode(encoding='utf-8'))


			#Pega a resposta do servidor sobre a jogada do usuario
			res = ttc.get_msg_from_socket(s, exception=False, ex=True)


			# se for um erro, pergunta a jogada normalmente
			if is_error_in_answer(res):
				print("Servidor não está gostando da resposta, tente de novo.\n")
				continue;
			else:
				ttc.apply_turn(turn_json, gf, ttc.USER_RAW_STEP)
				ttc.print_game_field(gf)


			# Procura por ganhadores, se tiver um o jogo termina
			handle_winner_variable(res)


			#Pega a jogada do servidor
			print("Esperando a resposta do servidor...")
			server_step = ttc.get_msg_from_socket(s)
			ttc.d("server step: {0}\n".format(server_step))
			ttc.apply_turn(server_step, gf, ttc.SERVER_RAW_STEP)
			handle_winner_variable(server_step)

			ttc.print_game_field(gf)


	except KeyboardInterrupt as k:
		print ("\nDesligando... {0}".format(k))
	except Exception as exp:
		print(": {0}".format(exp))
		ttc.print_game_field(gf)
	except:
		print("Erro inesperado:", sys.exc_info()[0])


	s.close()
	sys.exit(0)


# --------------------------------------------------------------------------- #
# ------------------------------- H E L P E R S ----------------------------- #
# --------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #

def is_error_in_answer (msg):


	try:
		ttc.d("your step validation: {0}".format(msg))
		tmp = json.loads(msg)

		if tmp["error"] == 1:
			return True

	except Exception as exp:
		print("eeem, {0}".format(exp))
		return False

# --------------------------------------------------------------------------- #

def handle_winner_variable (res):


	try:
		tmp = json.loads(res)
		winner = tmp["winner"]

		if 0 == winner :
			pass
		elif 1 == winner:
			raise Exception("Desculpas, mas você perdeu... =\\")
		elif 2 == winner:
			raise Exception("Você ganhou!")
		elif 3 == winner:
			raise Exception("Deu velha! (Empate)")
		else:
			print("Valor inesperado")

	except (KeyError, TypeError) as e:
		ttc.d(e)

# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #

if __name__ == "__main__":

	#Ip do servidor
	ttc.SERVER_IP = '192.168.0.16'

	#porta do servidor em execução
	ttc.SERVER_PORT = 9999


	main()
