from random import randrange

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет инжира
FIG_COLOR = (128, 0, 128)

# Цвет каменной стены
WALL_COLOR = (120, 120, 120)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject():
    """Базовый класс, на его основании созданы остальные"""

    def __init__(self) -> None:
        """Метод инициации объекта"""
        # Атрибут цвета объекта
        self.body_color = None
        # Атрибут позиции объекта, базовое значение - по центру экрана
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

    def draw(self):
        """Заготовка под наследуемый метод"""
        pass


class Snake(GameObject):
    """Класс отвечающий за поведение объекта змейки"""

    def __init__(
            self, length=1,
            object_position=[(320, 240)], direction=RIGHT,
            next_direction=None
    ):
        """Метод инициации экземпяра класса змейки"""
        super().__init__()
        self.positions = object_position
        self.body_color = SNAKE_COLOR
        self.length = length  # Атрибут максимальной длины змейки в дан. мом-нт
        self.direction = direction  # Атрибут направления движения змейки
        self.next_direction = next_direction  # Атрибут направления в след. тик
        self.last = None  # Атрибут для закрашивания последней клетки при дв-ии
        self.difficulty = 1  # Атрибут сложности игры

    def draw(self):
        """Метод визуализации змейки и стирания ее хвоста при движении"""
        # Отрисовка тела
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)
        # Отрисовка головы
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)
        # Закрашивание последнего квадрата для сим-ии движения
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def update_direction(self):
        """Метод для обновления направления змейки"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Метод реализует логику движения змейки и перехода через край поля"""
        new_head_position = (
            self.get_head_position()[0] + GRID_SIZE * self.direction[0],
            self.get_head_position()[1] + GRID_SIZE * self.direction[1]
        )
        # Обработка случаев выхода за край экрана
        if new_head_position[0] < 0:
            new_head_position = (
                new_head_position[0] + SCREEN_WIDTH, new_head_position[1])
        if new_head_position[0] >= SCREEN_WIDTH:
            new_head_position = (
                new_head_position[0] - SCREEN_WIDTH, new_head_position[1])
        if new_head_position[1] < 0:
            new_head_position = (
                new_head_position[0], new_head_position[1] + SCREEN_HEIGHT)
        if new_head_position[1] >= SCREEN_HEIGHT:
            new_head_position = (
                new_head_position[0], new_head_position[1] - SCREEN_HEIGHT)
        # Вставляем новую голову змейки в начало списка
        self.positions.insert(0, new_head_position)
        # Назначаем квадратик, который предстоит стереть
        self.last = self.positions[-1]
        # Проверка длины для случая поедания инжиров
        while len(self.positions) > self.length:
            dropped_tail = pygame.Rect(
                self.positions.pop(), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, dropped_tail)

    def get_head_position(self):
        """Метод возвращает позицию головы змейки"""
        return self.positions[0]

    def reset(self):
        """Метод возвращает змейку к исходному состоянию"""
        self.positions = [(320, 240)]
        self.length = 1
        self.direction = RIGHT


class Apple(GameObject):
    """Класс Яблока - полезная еда, увеличивающая длину змейки на 1"""

    def __init__(self):
        """Метод инициализации экземпляра класса"""
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def randomize_position(self):
        """Метод задания случайных координат в пределах игрового поля"""
        coordinates = (randrange(20, 619, 20), randrange(20, 420, 20))
        self.position = coordinates

    def draw(self):
        """Метод визуализации яблока"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Fig(Apple):
    """Класс Инжир - вредная еда, уменьшающая длину змейки на 1"""

    def __init__(self):
        """Метод инициализации экземпляра класса"""
        super().__init__()
        self.body_color = FIG_COLOR


class StoneWall(Apple):
    """Класс каменная стена - препятствие, при столкновении обнуляет игру"""

    def __init__(self):
        """Метод инициализации экземпляра класса"""
        super().__init__()
        self.body_color = WALL_COLOR
        if randrange(1, 3) > 1:  # Выбираем случайное направление стены
            self.direction = DOWN
        else:
            self.direction = RIGHT
        # Удлинняем стену в выбранном направлении
        self.positions = [
            (self.position[0] + self.direction[0] * GRID_SIZE * i,
             self.position[1] + self.direction[1] * GRID_SIZE * i
             ) for i in range(9)]

    def draw(self):
        """Метод визуализации инжира"""
        for position in self.positions:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


# Набор функций ответа на нажатия клавиш пользователем
def k_escape_event(game_object):
    """функция при нажатии клавиши ESC"""
    pygame.quit()
    raise SystemExit


def k_up_event(game_object):
    """функция при нажатии клавиши UP"""
    if game_object.direction != DOWN:
        game_object.next_direction = UP


def k_down_event(game_object):
    """функция при нажатии клавиши DOWN"""
    if game_object.direction != UP:
        game_object.next_direction = DOWN


def k_left_event(game_object):
    """функция при нажатии клавиши LEFT"""
    if game_object.direction != RIGHT:
        game_object.next_direction = LEFT


def k_right_event(game_object):
    """функция при нажатии клавиши RIGHT"""
    if game_object.direction != LEFT:
        game_object.next_direction = RIGHT


def k_1_event(game_object):
    """Установить 1 сложность. Инжиров - 1. Нет стены. Скорость 10"""
    game_object.difficulty = 1
    screen.fill(BOARD_BACKGROUND_COLOR)
    game_object.reset()


def k_2_event(game_object):
    """Установить 2 сложность. Инжиров - 3. Стена. Скорость 20"""
    game_object.difficulty = 2
    screen.fill(BOARD_BACKGROUND_COLOR)
    game_object.reset()


# Cловарь с ключами - нажатиями клавиш и значениями - функциями,
#  которые они исполняют
key_functions = {
    pygame.K_ESCAPE: k_escape_event,
    pygame.K_UP: k_up_event,
    pygame.K_DOWN: k_down_event,
    pygame.K_LEFT: k_left_event,
    pygame.K_RIGHT: k_right_event,
    pygame.K_1: k_1_event,
    pygame.K_2: k_2_event
}


def handle_keys(game_object):
    """Функция обрабатывает ввод пользователя при помощи словаря функций"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            k_escape_event(game_object)
        elif event.type == pygame.KEYDOWN:
            key_functions[event.key](game_object)


def check_figs(snake, *figs):
    """Вспомогательная функция для цикла игры, проверяет поедание инжира"""
    for fig in figs:
        if snake.positions[0] == fig.position:
            if snake.length > 1:
                snake.length -= 1
            fig.randomize_position()


def game_cycle_easy(object_snake, object_fig1, object_fig2, object_fig3,
                    object_stone_wall, object_apple, game_speed):
    """Цикл игры при сложности 1"""
    clock.tick(game_speed - 10)
    # Убираем доп инжиры и стену с карты пока сложность низкая
    object_fig2.position = (1000, 1000)
    object_fig3.position = (1200, 1200)
    object_stone_wall.position = (1300, 1300)
    handle_keys(object_snake)
    object_snake.update_direction()
    object_snake.move()
    # Проверка "Съели яблоко"
    if object_snake.positions[0] == object_apple.position:
        object_snake.length += 1
        object_apple.randomize_position()
    # Проверка "Столкнулись с собой"
    if object_snake.positions[0] in object_snake.positions[1:]:
        screen.fill(BOARD_BACKGROUND_COLOR)
        object_snake.reset()
    # Проверка на плохую еду
    check_figs(object_snake, object_fig1)
    object_snake.draw()
    object_apple.draw()
    object_fig1.draw()
    pygame.display.update()


def game_cycle_hard(object_snake, object_fig1, object_fig2, object_fig3,
                    object_stone_wall, object_apple, game_speed):
    """Цикл игры при сложности 2"""
    clock.tick(game_speed)
    # Возвращаем доп инжиры, пока сложность высокая
    if object_fig2.position[0] > 900:
        object_fig2.randomize_position()
    if object_fig3.position[0] > 900:
        object_fig3.randomize_position()
    # Возвращаем стену, пока сложность высокая
    if object_stone_wall.position[0] > 900:
        object_stone_wall.randomize_position()
    object_fig2.draw()
    object_fig3.draw()
    object_stone_wall.draw()
    handle_keys(object_snake)
    object_snake.update_direction()
    object_snake.move()
    # Проверка "Съели яблоко"
    if object_snake.positions[0] == object_apple.position:
        object_snake.length += 1
        object_apple.randomize_position()
    # Проверка "Столкнулись с собой"
    if object_snake.positions[0] in object_snake.positions[1:]:
        screen.fill(BOARD_BACKGROUND_COLOR)
        object_snake.reset()
    # Проверка на плохую еду
    check_figs(object_snake, object_fig1, object_fig2, object_fig3)
    if object_snake.positions[0] in object_stone_wall.positions:  # Проверяем
        screen.fill(BOARD_BACKGROUND_COLOR)  # Столкновение со стеной
        object_snake.reset()
    object_snake.draw()
    object_apple.draw()
    object_fig1.draw()
    pygame.display.update()


def main():
    """Функция с основной логикой игры"""
    # Инициализация PyGame:
    pygame.init()
    # Создаем объекты классов
    apple = Apple()
    snake = Snake()
    fig1 = Fig()
    fig2 = Fig()
    fig3 = Fig()
    stonewall = StoneWall()
    # Выводим дополнительные объекты за пределы до момента повышения сложности
    fig2.position = (1000, 1000)
    fig3.position = (1200, 1200)
    stonewall.position = (1300, 1300)
    # Располагаем и отрисовываем основные объекты на экране
    fig1.randomize_position()
    apple.randomize_position()
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
