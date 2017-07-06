# -*- coding: utf-8 -*-

from __future__ import print_function
import tic_tac_common as ttc

import socket
import sys,  time
import json, random, copy, argparse

#Verifique o final do arquivo para configurar a porta

# ---------------------------------------------------------------------------- #


MULTIPLAYER_MODE=0

# ---------------------------------------------------------------------------- #


def main():

	s = get_server_socket()

	try:
		### Loop infinito para multiplos jogos
		while True:

			print ('Esperando um jogador...')
			(clientsocket, address) = s.accept() # bloqueio de linha aqui
			print ('Novo jogador vindo de {0}\n'.format(address))
			clientsocket.sendall("Servidor de Jogo da velha!\nSeja bem vindo!".encode(encoding='UTF-8'))

			gf = copy.deepcopy(ttc.GAME_FIELD)

			### um jogo, loop termina caso haja um vencedor
			while True:


				#Pega a jogada do usuário
				try:
					print("Esperando o turno do usuario")
					user_step = ttc.get_msg_from_socket(clientsocket, exception=True, ex=False)
				except Exception as exp:
					ttc.d(exp)
					ttc.d("\n" + 40*"=" + "\n")
					break;


				#valida jogada#
				step_check = {}

				ttc.d("user raw turn: {}".format(user_step))



				step_check["error"] = not ttc.is_step_correct(user_step, gf)


				if not step_check["error"]:
					ttc.apply_turn(user_step, gf, ttc.USER_RAW_STEP)
					step_check["winner"] = get_winner(gf)
					ttc.print_game_field(gf)
				else:
					step_check["winner"] = 0


				#B resposta se a jogada está correta #
				step_check_str = json.dumps(step_check)
				ttc.d("I will send: {0}".format(step_check_str))
				clientsocket.sendall(step_check_str.encode(encoding='UTF-8'))
				time.sleep(0.1)


				# se ocorrer um erro pede uma nova resposta do usuário
				if True == step_check["error"] or 0 != step_check["winner"]:
					continue;

				# Jogada do servidor#
				ttc.d("proceed server turn")

				server_step_dict = do_server_step(gf)
				ttc.d("server step: {}".format(server_step_dict))
				ttc.apply_turn(json.dumps(server_step_dict), gf, ttc.SERVER_RAW_STEP)



				# Valida se há algum ganhador
				server_step_dict["winner"] = get_winner(gf)
				server_step_dict["error"]  = False


				#B manda a jogada do servidor com a resposta de quem venceu
				clientsocket.sendall( json.dumps(server_step_dict).encode(encoding='UTF-8') )


				ttc.print_game_field(gf)


	except KeyboardInterrupt as exp:
		print ("\nDesligando... {0}".format(exp))
	except Exception as exp:
		print("Desculpas, mas: {0}".format(exp))
	except:
		print("Erro inesperado:", sys.exc_info()[0])



	try:
		clientsocket.close()
		s.close()
	except Exception as exp:
		# Não é um erro mas...
		ttc.d("Você podera se interessar, mas {0}".format(exp))

	sys.exit(0)





# ---------------------------------------------------------------------------- #
# -------------------- H E L P E R S ----------------------------------------- #
# ---------------------------------------------------------------------------- #

def get_server_socket ():


	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		my_hostname = socket.gethostname()
		s.bind((my_hostname, ttc.SERVER_PORT))
		# permite 1 conexão por vez
		s.listen(1)
		print("Servidor rodando em {0}:{1}\n".format(my_hostname, ttc.SERVER_PORT))
		return s
	except Exception as exp:
		print("Impossível de iniciar socket em {0}:{1}".format(ttc.SERVER_IP, ttc.SERVER_PORT))
		print("~> %s" %exp)
		sys.exit(1)



# ---------------------------------------------------------------------------- #
# ---------------------------- L O G I C ------------------------------------- #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
def it_is_first_server_turn (game_field):


	count = 0

	for line in game_field:
		count += line.count(ttc.EMPTY_RAW_STEP)

	if count == 8:
		return True
	else:
		return False

# --------------------------------------------------------------------------- #

def has_line_with_two_moves(game_field, move_kind):


	gf = game_field
	length = len(game_field)


	# verifica linhas e colunas

	for j in range(length):
		# pega as linhas e colunas como listas
		row = [ gf[j][i] for i in range(length) ]
		col = [ gf[i][j] for i in range(length) ]

		if row.count(move_kind) == 2 and row.count(ttc.EMPTY_RAW_STEP) == 1:
			return [True, [j, row.index(ttc.EMPTY_RAW_STEP)] ]

		if col.count(move_kind) == 2 and col.count(ttc.EMPTY_RAW_STEP) == 1:
			return [True, [col.index(ttc.EMPTY_RAW_STEP), j] ]


	# verifica as diagonais
	diag_1 = [ gf[0][0], gf[1][1], gf[2][2] ]
	if diag_1.count(move_kind) == 2 and diag_1.count(ttc.EMPTY_RAW_STEP) == 1:
		i = diag_1.index(ttc.EMPTY_RAW_STEP)
		return [ True, [i, i] ]

	diag_2 = [ gf[2][0], gf[1][1], gf[0][2] ]
	if diag_2.count(move_kind) == 2 and diag_2.count(ttc.EMPTY_RAW_STEP) == 1:
		j = diag_2.index(ttc.EMPTY_RAW_STEP)
		i = -j + 2
		return [ True, [i, j] ]

	# oh no =\
	return [ False, [-1, -1] ]


# --------------------------------------------------------------------------- #

def do_server_step (game_field):

	tmp = {}

	cell=()
	if it_is_first_server_turn(game_field):
		i = 0
		for line in game_field:
			if 0 != line.count( ttc.USER_RAW_STEP ):
				cell = ( i, line.index(ttc.USER_RAW_STEP) )
			i += 1

		ttc.d("How server see the cell of user first turn {0}".format(cell))

		if cell==(0,0) or cell==(0,2) or cell==(2,0) or cell==(2,2):
			tmp["step"] = [1, 1]
		else:
			tmp["step"] = [0, 0]

		return tmp



	has_line_with_2_friendly_cells = has_line_with_two_moves(game_field, ttc.SERVER_RAW_STEP)
	if has_line_with_2_friendly_cells[0]:
		tmp["step"] = has_line_with_2_friendly_cells[1]
		ttc.d("step 2 attack {0}".format(tmp["step"]))
		return tmp



	has_line_with_2_enemy_cell = has_line_with_two_moves(game_field, ttc.USER_RAW_STEP)
	if has_line_with_2_enemy_cell[0]:
		tmp["step"] = has_line_with_2_enemy_cell[1]
		ttc.d("step 2 def {0}".format(tmp["step"]))
		return tmp







	random.seed()
	tmp["step"] = [random.randrange(3), random.randrange(3)]

	while True:
		tmp_json_str = json.dumps(tmp)
		ttc.d("server step: {0}".format(tmp_json_str))
		if not ttc.is_step_correct(tmp_json_str, game_field):
			tmp["step"] = [random.randrange(3), random.randrange(3)]
			continue
		else:
			break

	return tmp
# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #

def get_winner (game_field):


	winner = 0
	gf = game_field  # weak reference

	empty = ttc.EMPTY_RAW_STEP	# 1
	cross = ttc.USER_RAW_STEP 	# 2
	zeros  = ttc.SERVER_RAW_STEP	# 5

	length = len(game_field)


	try:
		### verifica se há ganhador

		# pelas colunas e linhas
		for j in range(length):
			row = [ gf[j][i] for i in range(length) ]
			col = [ gf[i][j] for i in range(length) ]
			if col.count(cross) == length or row.count(cross) == length:
				winner = 2
				raise Exception("User wins!")
			elif col.count(zeros) == length or row.count(zeros) == length:
				winner = 1
				raise Exception("Server wins!")


		# pelas diagonais
		for diag in [ [gf[0][0], gf[1][1], gf[2][2]], [gf[0][2], gf[1][1], gf[2][0]] ]:
			if diag.count(cross) == length:
				winner = 2
				raise Exception("User wins!")
			elif diag.count(zeros) == length:
				winner = 1
				raise Exception("Server wins!")


		### verifica por empate contando os espaços vazios nas colunas
		empty_count = 0
		for line in game_field:
			empty_count += line.count(empty)
		if 0 == empty_count:
			winner = 3
			raise Exception("Empate, sem campos vazios")


	except Exception as ex:
		# do nothing, just goto
		ttc.d(ex)


	return winner




# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #

if __name__ == "__main__":
    #porta em que o servidor irá rodar
    ttc.SERVER_PORT = 9999

    #Modo multiplayer
    MULTIPLAYER_MODE = 1
    main()
