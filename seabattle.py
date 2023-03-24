# -*- coding: utf-8 -*-

from random import randint

######################################################################################################################


class BoardException(Exception):
	pass


######################################################################################################################


class Dot:
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __eq__(self, other):
		return self.x == other.x and self.y == other.y


######################################################################################################################


class Ship:
	def __init__(self, bow, length, orientation):
		self.bow = bow
		self.length = length
		self.orientation = orientation
		self.lives = length

	@property
	def dots(self):
		ship_dots = []
		for i in range(self.length):
			current_x = self.bow.x
			current_y = self.bow.y
			if self.orientation == 0:
				current_x += i
			elif self.orientation == 1:
				current_y += i
			ship_dots.append(Dot(current_x, current_y))
		return ship_dots


######################################################################################################################


class Board:
	def __init__(self, dimension=6, hide=False):
		self.dimension = dimension
		self.hide = hide
		self.count = 0
		self.field = [['O'] * dimension for _ in range(dimension)]
		self.busy = []
		self.ships = []

	def add_ship(self, ship):
		for dot in ship.dots:
			if self.out(dot) or dot in self.busy:
				raise BoardException()
		for dot in ship.dots:
			self.field[dot.x][dot.y] = '■'
			self.busy.append(dot)
		self.ships.append(ship)
		self.mark_contour(ship)

	def mark_contour(self, ship, verb=False):
		near = [
			(-1, -1), (-1, 0), (-1, 1),
			(0, -1), (0, 0), (0, 1),
			(1, -1), (1, 0), (1, 1)
		]
		for dot in ship.dots:
			for dx, dy in near:
				dot_contour = Dot(dot.x + dx, dot.y + dy)
				if not self.out(dot_contour) and dot_contour not in self.busy:
					if verb:
						self.field[dot_contour.x][dot_contour.y] = 'T'
					self.busy.append(dot_contour)

	def out(self, dot):
		return not ((0 <= dot.x < self.dimension) and (0 <= dot.y < self.dimension))

	def shot(self, dot):
		if self.out(dot):
			raise BoardException('Вы указали координаты за пределом поля!')
		if dot in self.busy:
			raise BoardException('Эти координаты уже стреляли по этим координатам.')
		self.busy.append(dot)
		for ship in self.ships:
			if dot in ship.dots:
				ship.lives -= 1
				self.field[dot.x][dot.y] = 'X'
				if ship.lives == 0:
					self.count += 1
					self.mark_contour(ship, verb=True)
					print('Корабль уничтожен!')
					return False
				else:
					print('Корабль ранен!')
					return True
		self.field[dot.x][dot.y] = 'T'
		print('Промах!')
		return False

	def begin(self):
		self.busy = []


######################################################################################################################


class Player:
	def __init__(self, self_board, enemy_board):
		self.self_board = self_board
		self.enemy_board = enemy_board

	def request_move(self):
		raise NotImplementedError()

	def move(self):
		while True:
			try:
				target = self.request_move()
				repeat = self.enemy_board.shot(target)
				return repeat
			except BoardException as ex:
				print(f'Ошибка: {ex}')


######################################################################################################################


class AI(Player):
	def request_move(self):
		while True:
			dot = Dot(randint(0, 5), randint(0, 5))
			if dot not in self.enemy_board.busy:
				print(f'Ход компьютера: {dot.x + 1} {dot.y + 1}')
				return dot


######################################################################################################################


class User(Player):
	def request_move(self):
		while True:
			coords = input('Введите координаты хода, две цифры через пробел, строку и столбец: ').split()
			if len(coords) == 2:
				row, col = coords
				if row.isdigit() and col.isdigit():
					row, col = int(row), int(col)
					return Dot(row - 1, col - 1)
				else:
					raise BoardException('Введите цифры.')
			else:
				raise BoardException('Введите 2 координаты!')


######################################################################################################################


class SeaBattle:
	def __init__(self, dimension=6, length_ships=[3, 2, 2, 1, 1, 1, 1]):
		self.dimension = dimension
		self.length_ships = length_ships
		player_board = self.random_board()
		computer_board = self.random_board()
		computer_board.hide = True
		self.user = User(self_board=player_board, enemy_board=computer_board)
		self.ai = AI(self_board=computer_board, enemy_board=player_board)

	def random_board(self):
		board = None
		while board is None:
			board = self.random_place()
		return board

	def random_place(self):
		board = Board(dimension=self.dimension)
		attempts = 0
		for length_ship in self.length_ships:
			while True:
				attempts += 1
				if attempts > 2000:
					return None
				ship = Ship(
					bow=Dot(randint(0, self.dimension), randint(0, self.dimension)),
					length=length_ship,
					orientation=randint(0, 1)
				)
				try:
					board.add_ship(ship)
					break
				except BoardException:
					pass
		board.begin()
		return board

	def print_board(self):
		print('-' * 60)
		print('  Поле Ваших кораблей:\t\t\t  Поле кораблей компьютера:')
		print('  | 1 | 2 | 3 | 4 | 5 | 6 |\t\t  | 1 | 2 | 3 | 4 | 5 | 6 |')
		for i, line in enumerate(zip(self.user.self_board.field, self.user.enemy_board.field)):
			line_player_field = f'{i + 1} | ' + ' | '.join(line[0]) + ' |'
			line_computer_filed = (f'{i + 1} | ' + ' | '.join(line[1]) + ' |').replace('■', 'O')
			print(f'{line_player_field}\t\t{line_computer_filed}')

	def start(self):
		step = 0
		while True:
			self.print_board()
			repeat = self.user.move() if step % 2 == 0 else self.ai.move()
			if repeat:
				step -= 1
			if self.ai.self_board.count == 7:
				self.print_board()
				print('-' * 60 + '\nВы выиграли! Поздравляем!')
				raise SystemExit(1)
			if self.user.self_board.count == 7:
				self.print_board()
				print('-' * 60 + '\nКомпьютер выиграл!')
				raise SystemExit(1)
			step += 1


######################################################################################################################


def main():
	game = SeaBattle(dimension=6, length_ships=[3, 2, 2, 1, 1, 1, 1])
	game.start()


######################################################################################################################


if __name__ == '__main__':
	main()

######################################################################################################################
