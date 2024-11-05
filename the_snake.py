from random import randrange

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_MIDDLE = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Константы цветов:
BLACK = (0, 0, 0)
RED = (255, 0, 0)
LIGHTBLUE = (93, 216, 228)
PURPLE = (128, 0, 128)
GREY = (120, 120, 120)
GREEN = (0, 255, 0)

# Константы цветов игровых объектов
BOARD_BACKGROUND_COLOR = BLACK
BORDER_COLOR = LIGHTBLUE
APPLE_COLOR = RED
FIG_COLOR = PURPLE
WALL_COLOR = GREY
SNAKE_COLOR = GREEN

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс, на его основании созданы остальные."""

    def __init__(
        self, object_color=None, object_position=SCREEN_MIDDLE
    ) -> None:
        """
        Метод инициации объекта. Базовые атрибуты - цвет (body_color)
        и позиция (position) объекта.
        """
        self.body_color = object_color
        self.position = object_position

    def draw(self):
        """Заготовка под наследуемый метод."""
        raise NotImplementedError

    def draw_rect(self, position, color=BOARD_BACKGROUND_COLOR):
        """Отрисовка прямоугольника в заданной позиции и заданного цвета"""
        rect = (pg.Rect(position, (GRID_SIZE, GRID_SIZE)))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, color, rect, 1)


class Snake(GameObject):
    """Класс отвечающий за поведение объекта змейки."""

    def __init__(
            self, length=1,
            object_position=SCREEN_MIDDLE,
            direction=RIGHT,
            next_direction=None,
            body_color=SNAKE_COLOR
    ):
        """
        Метод инициации экземпяра класса змейки.
        Атрибут length - максимальная длина змейки в данный момент
        Атрибут direction - направление змейки
        Атрибут next_direction - направление в следующий тик
        Атрибут last - для закрашивания последней клетки при движении
        Атрибут difficulty - текущий уровень сложности игры, влияет на наличие
        стены, скорость игры и количество инжиров
        """
        super().__init__()
        self.positions = [object_position]
        self.body_color = body_color
        self.next_direction = next_direction
        self.last = None
        self.difficulty = 1
        self.reset()

    def draw(self):
        """Метод визуализации змейки и стирания ее хвоста при движении."""
        # Отрисовка головы
        self.draw_rect(self.positions[0], BORDER_COLOR)
        # Закрашивание последнего квадрата для сим-ии движения
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
        # Проверка на поедание инжира
        while len(self.positions) > self.length:
            dropped_tail = pg.Rect(
                self.positions.pop(), (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, dropped_tail)

    def update_direction(self):
        """Метод для обновления направления змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """
        Метод реализует логику движения змейки
        и перехода через край поля.
        """
        new_head_position = (
            (self.get_head_position()[0] + GRID_SIZE
             * self.direction[0]) % SCREEN_WIDTH,
            (self.get_head_position()[1] + GRID_SIZE
             * self.direction[1]) % SCREEN_HEIGHT
        )
        # Вставляем новую голову змейки в начало списка
        self.positions.insert(0, new_head_position)
        # Назначаем квадратик, который предстоит стереть
        self.last = self.positions[-1]

    def get_head_position(self):
        """Метод возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Метод возвращает змейку к исходному состоянию."""
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT


class Apple(GameObject):
    """Класс Яблока - полезная еда, увеличивающая длину змейки на 1."""

    def __init__(self, color=APPLE_COLOR, occupied_cells=SCREEN_MIDDLE):
        """Метод инициализации экземпляра класса."""
        super().__init__()
        self.body_color = color
        self.randomize_position(occupied_cells=occupied_cells)

    def randomize_position(self, occupied_cells=[SCREEN_MIDDLE]):
        """Метод задания случайных координат в пределах игрового поля."""
        coordinates = (randrange(20, SCREEN_WIDTH, 20),
                       randrange(20, SCREEN_HEIGHT, 20))
        while coordinates in occupied_cells:
            coordinates = (randrange(20, SCREEN_WIDTH, 20),
                           randrange(20, SCREEN_HEIGHT, 20))
        self.position = coordinates

    def draw(self):
        """Метод визуализации яблока."""
        self.draw_rect(self.position, BORDER_COLOR)


class Fig(Apple):
    """Класс Инжир - вредная еда, уменьшающая длину змейки на 1."""

    def __init__(self, color=FIG_COLOR):
        """Метод инициализации экземпляра класса."""
        super().__init__()
        self.body_color = color
        self.randomize_position()


class StoneWall(Apple):
    """Класс каменная стена - препятствие, при столкновении обнуляет игру."""

    def __init__(self, color=WALL_COLOR):
        """Метод инициализации экземпляра класса."""
        super().__init__()
        self.body_color = color
        # Выбираем случайное направление стены
        self.choose_direction()
        # Удлинняем стену в выбранном направлении
        self.positions = [
            (self.position[0] + self.direction[0] * GRID_SIZE * i,
             self.position[1] + self.direction[1] * GRID_SIZE * i
             ) for i in range(9)]
        self.randomize_position()

    def choose_direction(self):
        """Выбираем случайное направление для стены в координатах поля."""
        if randrange(1, 3) > 1:
            self.direction = DOWN
        else:
            self.direction = RIGHT

    def draw(self):
        """Метод визуализации инжира."""
        for position in self.positions:
            self.draw_rect(position, BORDER_COLOR)


# Набор функций ответа на нажатия клавиш пользователем
def k_escape_event(game_object):
    """функция при нажатии клавиши ESC."""
    pg.quit()
    raise SystemExit


def k_up_event(game_object, key):
    """функция при нажатии клавиши UP."""
    if key == pg.K_UP and game_object.direction != DOWN:
        game_object.next_direction = UP
    if key == pg.K_DOWN and game_object.direction != UP:
        game_object.next_direction = DOWN
    if key == pg.K_LEFT and game_object.direction != RIGHT:
        game_object.next_direction = LEFT
    if key == pg.K_RIGHT and game_object.direction != LEFT:
        game_object.next_direction = RIGHT
    game_object.update_direction()


def k_1_event(game_object, key):
    """Установить 1 сложность. Инжиров - 1. Нет стены. Скорость 10."""
    game_object.difficulty = 1
    screen.fill(BOARD_BACKGROUND_COLOR)
    game_object.reset()


def k_2_event(game_object, key):
    """Установить 2 сложность. Инжиров - 3. Стена. Скорость 20."""
    game_object.difficulty = 2
    screen.fill(BOARD_BACKGROUND_COLOR)
    game_object.reset()


# Cловарь с ключами - нажатиями клавиш и значениями - функциями,
#  которые они исполняют
key_functions = {
    pg.K_ESCAPE: k_escape_event,
    pg.K_UP: k_up_event,
    pg.K_DOWN: k_up_event,
    pg.K_LEFT: k_up_event,
    pg.K_RIGHT: k_up_event,
    pg.K_1: k_1_event,
    pg.K_2: k_2_event
}


def handle_keys(game_object):
    """Функция обрабатывает ввод пользователя при помощи словаря функций."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            k_escape_event(game_object)
        elif event.type == pg.KEYDOWN:
            if event.key in key_functions.keys():
                key_functions[event.key](game_object, event.key)


def check_figs(snake, *figs):
    """Вспомогательная функция для цикла игры, проверяет поедание инжира."""
    for fig in figs:
        if snake.positions[0] == fig.position:
            if snake.length > 1:
                snake.length -= 1
            fig.randomize_position(snake.positions)


def game_cycle_decorator(func):
    """Декоратор общих для всех уровней слонжости действий цикла игры."""
    def wrapper(object_snake, object_fig1, object_fig2, object_fig3,
                object_stone_wall, object_apple, game_speed):
        result = func(object_snake, object_fig1, object_fig2, object_fig3,
                      object_stone_wall, object_apple, game_speed)
        handle_keys(object_snake)
        object_snake.move()
        # Проверка "Съели яблоко"
        if object_snake.get_head_position() == object_apple.position:
            object_snake.length += 1
            object_apple.randomize_position(object_snake.positions)
        # Проверка "Столкнулись с собой"
        elif object_snake.get_head_position() in object_snake.positions[3:]:
            screen.fill(BOARD_BACKGROUND_COLOR)
            object_snake.reset()
        # Проверка на плохую еду
        check_figs(object_snake, object_fig1, object_fig2, object_fig3)
        object_snake.draw()
        object_apple.draw()
        object_fig1.draw()
        pg.display.update()
        return result
    return wrapper


@game_cycle_decorator
def game_cycle_easy(object_snake, object_fig1, object_fig2, object_fig3,
                    object_stone_wall, object_apple, game_speed):
    """Цикл игры при сложности 1."""
    if object_fig2:
        del object_fig2
        del object_fig3
        del object_stone_wall
    clock.tick(game_speed - 10)
    # Убираем доп инжиры и стену с карты пока сложность низкая


@game_cycle_decorator
def game_cycle_hard(object_snake, object_fig1, object_fig2, object_fig3,
                    object_stone_wall, object_apple, game_speed):
    """Цикл игры при сложности 2."""
    clock.tick(game_speed)
    # Возвращаем доп инжиры, пока сложность высокая
    if not object_fig2:
        object_fig2 = Fig()
        object_fig3 = Fig()
        object_stone_wall = StoneWall()
    # Проверяем столкновение со стеной
    if object_snake.positions[0] in object_stone_wall.positions:
        screen.fill(BOARD_BACKGROUND_COLOR)
        object_snake.reset()
    object_fig2.draw()
    object_fig3.draw()
    object_stone_wall.draw()


def main():
    """Функция с основной логикой игры."""
    # Инициализация pg:
    pg.init()
    # Создаем объекты классов
    snake = Snake()
    apple = Apple(occupied_cells=snake.positions)
    fig1 = Fig()
    fig2 = Fig()
    fig3 = Fig()
    stonewall = StoneWall()
    # Располагаем и отрисовываем основные объекты на экране
    snake.draw()
    apple.draw()
    fig1.draw()
    # Входим в основной цикл игры
    while True:  # При каждом шаге цикла идет проверка уровня сложности
        if snake.difficulty == 1:
            game_cycle_easy(snake, fig1, fig2, fig3, stonewall, apple, SPEED)
        elif snake.difficulty == 2:
            game_cycle_hard(snake, fig1, fig2, fig3, stonewall, apple, SPEED)


if __name__ == '__main__':
    main()
