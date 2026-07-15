import turtle
import random

WIDTH = 600
HEIGHT = 400
CELL_SIZE = 20
DELAY = 100

UP = "Up"
DOWN = "Down"
LEFT = "Left"
RIGHT = "Right"

def main():
    global snake, food, direction, score, game_over, score_board
    
    window = turtle.Screen()
    window.title("贪吃蛇游戏")
    window.setup(WIDTH, HEIGHT)
    window.bgcolor("black")
    window.tracer(0)
    
    snake_head = turtle.Turtle()
    snake_head.shape("square")
    snake_head.color("white")
    snake_head.penup()
    snake_head.goto(0, 0)
    
    food = turtle.Turtle()
    food.shape("circle")
    food.color("red")
    food.penup()
    spawn_food()
    
    score = 0
    score_board = turtle.Turtle()
    score_board.color("white")
    score_board.penup()
    score_board.hideturtle()
    score_board.goto(0, HEIGHT//2 - 30)
    score_board.write(f"分数: {score}", align="center", font=("Arial", 16, "normal"))
    
    snake = [snake_head]
    direction = RIGHT
    game_over = False
    
    window.listen()
    window.onkeypress(go_up, UP)
    window.onkeypress(go_down, DOWN)
    window.onkeypress(go_left, LEFT)
    window.onkeypress(go_right, RIGHT)
    
    while not game_over:
        window.update()
        move_snake()
        check_food()
        check_collision()
        turtle.delay(DELAY)
    
    score_board.clear()
    score_board.write(f"游戏结束! 分数: {score}", align="center", font=("Arial", 20, "bold"))
    
    window.mainloop()

def spawn_food():
    x = random.randint(-WIDTH//2 + CELL_SIZE, WIDTH//2 - CELL_SIZE)
    y = random.randint(-HEIGHT//2 + CELL_SIZE, HEIGHT//2 - CELL_SIZE)
    x = round(x / CELL_SIZE) * CELL_SIZE
    y = round(y / CELL_SIZE) * CELL_SIZE
    food.goto(x, y)

def go_up():
    global direction
    if direction != DOWN:
        direction = UP

def go_down():
    global direction
    if direction != UP:
        direction = DOWN

def go_left():
    global direction
    if direction != RIGHT:
        direction = LEFT

def go_right():
    global direction
    if direction != LEFT:
        direction = RIGHT

def move_snake():
    global direction
    
    head = snake[0]
    x, y = head.position()
    
    if direction == UP:
        y += CELL_SIZE
    elif direction == DOWN:
        y -= CELL_SIZE
    elif direction == LEFT:
        x -= CELL_SIZE
    elif direction == RIGHT:
        x += CELL_SIZE
    
    head.goto(x, y)
    
    for i in range(len(snake)-1, 0, -1):
        prev_x, prev_y = snake[i-1].position()
        snake[i].goto(prev_x, prev_y)

def check_food():
    global score
    
    head = snake[0]
    if head.distance(food) < CELL_SIZE:
        score += 10
        score_board.clear()
        score_board.write(f"分数: {score}", align="center", font=("Arial", 16, "normal"))
        spawn_food()
        
        new_segment = turtle.Turtle()
        new_segment.shape("square")
        new_segment.color("gray")
        new_segment.penup()
        snake.append(new_segment)

def check_collision():
    global game_over
    
    head = snake[0]
    x, y = head.position()
    
    if x < -WIDTH//2 or x > WIDTH//2 - CELL_SIZE or \
       y < -HEIGHT//2 or y > HEIGHT//2 - CELL_SIZE:
        game_over = True
    
    for segment in snake[1:]:
        if head.distance(segment) < CELL_SIZE:
            game_over = True

if __name__ == "__main__":
    main()