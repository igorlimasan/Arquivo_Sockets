# -*- coding: utf-8 -*-


from __future__ import print_function
import socket
import sys
import json, re


SERVER_IP   = 'localhost'
SERVER_PORT =  64501

# 1 : Vazio
# 2 : X
# 5 : O

GAME_FIELD = [
	[1, 1, 1],
	[1, 1, 1],
	[1, 1, 1]
]

EMPTY_RAW_STEP = 1
USER_RAW_STEP  = 2
SERVER_RAW_STEP= 5

EMPTY_RAW   = "*"
USER_STEP   = "X"
SERVER_STEP = "O"

DEBUG = 0

# --------------------------------------------------------------------------- #

def print_game_field (board):
	for line in board:
		for cel in line:
			if cel == SERVER_RAW_STEP: print(SERVER_STEP, "\t", end='')
			if cel == USER_RAW_STEP  : print(USER_STEP, "\t",   end='')
			if cel == EMPTY_RAW_STEP : print(EMPTY_RAW, "\t",   end='')
		print('')
	print('')


# --------------------------------------------------------------------------- #

def get_msg_from_socket (socket, exception=True, ex=False):

	data = socket.recv(4096).decode(encoding='UTF-8')

	if not data:
		socket.close()

		if (exception):
			raise Exception("Conexão encerrada pelo ponto")
		else:
			print("Fechado pelo ponto.");

		if (ex):
			exit(1)

	return data

# --------------------------------------------------------------------------- #

def d (msg):
	if DEBUG != 0:
		print("D: {0}".format(msg))

# --------------------------------------------------------------------------- #

def get_turn_from_user (board):

	tmp_json = False
	while True:

		tmp = input(">: ")

		# Converte a jogada para JSON se correto
		tmp_json = convert_step_to_json(tmp, board)
		d(tmp_json)
		if tmp_json is False:
			print("Jogada ruim. por favor tente novamente\n")
			continue;
		break;

	return tmp_json

# --------------------------------------------------------------------------- #

def convert_step_to_json (msg, board):

	d("convert input: {}".format(msg))

	parts = re.split("\s*", msg)

	d("split into {}".format(parts))

	try:
		row = int(float(parts[0]))
		col = int(float(parts[1]))

		answer = {}
		answer["step"] = [row, col]
		tmp_json = json.dumps(answer)

		if not is_step_correct(tmp_json, board):
			raise Exception("Incorrect coordinates, sorry.")

	except Exception as exp:
		d("Oops: {0}".format(exp))
		return False

	return tmp_json

# --------------------------------------------------------------------------- #

def convert_json_turn_human_to_machine (user_turn_json):

	result_dict = {}
	result_dict["step"] = []

	try:
		tmp_dict = json.loads(user_turn_json)
		i = tmp_dict["step"][0] - 1
		j = tmp_dict["step"][1] - 1
		result_dict["step"] = [i, j]

	except Exception as exp:
		d("convert: {}".format(exp))


	return json.dumps(result_dict)

# --------------------------------------------------------------------------- #

def is_step_correct (user_step_json, gf):

	d("check: raw turn: {0}".format(user_step_json))

	try:
		# converte JSON para dicionário
		step_dict = json.loads(user_step_json)

		# converte para int
		i = int(float(step_dict["step"][0]))
		j = int(float(step_dict["step"][1]))

		# verifica jogada para os limites
		length = len(gf)
		if i >= length or i < 0 or j >= length or j < 0:
			raise Exception("Jogada ({0},{1}) está fora do campo de jogo.".format(i,j))

		# Se houver algum item naquela posição
		if gf[i][j] != EMPTY_RAW_STEP:
			texto = ''
			if gf[i][j] == 5:
				texto = 'O'
			else:
				texto = 'X'
			raise Exception("Na célula ({0},{1}) está {2} !".format(i, j, texto))

	except Exception as exp:
		print("uau, {0}".format(exp))
		return False

	return True

# --------------------------------------------------------------------------- #

def apply_turn (turn, board, data):


	try:
		tmp = json.loads(turn)
		i = tmp["step"][0]  # linha
		j = tmp["step"][1]  # coluna
		board[i][j] = data

	except Exception as exp:
		# it should never happend
		print(exp)
		print("Arrume")
		sys.exit(1)

# --------------------------------------------------------------------------- #

def get_client_socket (exception=False):

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		print("Conectando ao servidor em {}:{}.".format(SERVER_IP, SERVER_PORT))
		s.connect((SERVER_IP, SERVER_PORT))
		print("Conectado")
		return s
	except Exception as exp:
		if exception:
			raise Exception(exp)
		else:
			print("Parece que o servidor não está pronto =\\")
			print(exp)
			sys.exit(1)


# --------------------------------------------------------------------------- #
