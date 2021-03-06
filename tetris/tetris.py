#!usr/bin/env python3


import pygame
import random
import sys
from pathlib import Path


# Set Global Constants
WIDTH = 600
HEIGHT = 650
SIZE = (WIDTH, HEIGHT)
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_PX_WIDTH = 300
GRID_PX_HEIGHT = 600
BLOCK_SIZE = GRID_PX_HEIGHT // GRID_HEIGHT
TOP_LEFT_X = (WIDTH - GRID_PX_WIDTH) // 2
TOP_LEFT_Y = HEIGHT - GRID_PX_HEIGHT
INIT_FALL_SPEED = 1
MOVE_SPEED = 0.1
NEXT_TOP_LEFT_X = 490
NEXT_TOP_LEFT_Y = 150
CYCLES_TO_INCREASE_LEVEL = 50000

SCORE_REFERENCE = {'1': 40, '2': 100, '3': 300, '4': 1200}

scores_PATH = Path('scores.txt') 

# Colors:
BACKGROUND = (0, 0, 0) #BLACK
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 128, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (200, 0, 200)
RED = (255, 0, 0)
LGRAY = (30, 30, 30)
DGRAY = (185, 185, 185)
WHITE = (255, 255, 255)

# Piece Shapes and Colors
O = [[(0,0), (1,0), (0,1), (1,1)]]

Z = [[(0,0), (1,0), (1,1), (2,1)], 
     [(1,0), (0,1), (1,1), (0,2)]]

S = [[(0,0), (0,1), (1,1), (1,2)], 
     [(1,0), (2,0), (0,1), (1,1)]]

I = [[(-1,0), (0,0), (1,0), (2,0)], 
     [(0,-1), (0,0), (0,1), (0,2)]]

T = [[(0,0), (1,0), (2,0), (1,1)], 
     [(1,0), (0,1), (1,1), (1,2)], 
     [(1,0), (0,1), (1,1), (2,1)], 
     [(0,0), (0,1), (1,1), (0,2)]]

L = [[(0,0), (0,1), (0,2), (1,2)],
     [(0,0), (1,0), (2,0), (0,1)],
     [(0,0), (1,0), (1,1), (1,2)],
     [(2,0), (0,1), (1,1), (2,1)]]

J = [[(1,0), (1,1), (0,2), (1,2)],
     [(0,0), (0,1), (1,1), (2,1)],
     [(0,0), (1,0), (0,1), (0,2)],
     [(0,0), (1,0), (2,0), (2,1)]]

SHAPES = [O, Z, S, J, L, T, I]
SHAPE_COLORS = [YELLOW, RED, BLUE, GREEN, CYAN, PURPLE, ORANGE]


# Create input box class
class InputBox():
    """ Thanks to Timothy Downs """
    def get_key(self):
        while True:
            event = pygame.event.poll()
            if event.type == pygame.KEYDOWN:
                return event.key


    def display_box(self, window, message):
        font = pygame.font.SysFont('commicsans', 20)
        pygame.draw.rect(window, BACKGROUND, (100, 250, 200, 20), 0)
        pygame.draw.rect(window, WHITE, (98, 248, 204, 24), 1)
        if len(message) != 0:
            window.blit(font.render(message, 1, WHITE), (100, 250))
        pygame.display.update()


    def ask(self, window, question):
        pygame.font.init()
        current_string = []
        self.display_box(window, f'{question}: {"".join(current_string)}')
        running = True
        while running:
            inkey = self.get_key()
            if inkey == pygame.K_BACKSPACE:
                current_string = current_string[:-1]
            elif inkey == pygame.K_RETURN:
                break
            elif inkey <= 127:
                current_string.append(chr(inkey))
            self.display_box(window, f'{question}: {"".join(current_string)}')
        return "".join(current_string)


# Create Piece class
class Piece():
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.orientation = 0


# Create Game class:
class Game():
    """Represents the game itself and the playing loop """
    def __init__(self, name='player1'):
        # Initiate PyGame
        pygame.init()
        # Create display surface
        self.window = pygame.display.set_mode(SIZE) 
        pygame.display.set_caption('Tetrisish')
        #Generate pieces
        self.current_piece = self.get_piece()
        self.next_piece = self.get_piece()
        # Establish grid and filled_blocks dict
        self.filled_blocks = {}
        self.grid = self.make_grid()     
        # Initialize score
        self.score = 0
        # Initialize level
        self.level = 1
        # Initialize name
        self.name = name
        # Load previous scores
        self.scores = self.load_scores()
        self.max_score = self.get_max_score()
        # Set clock
        self.clock = pygame.time.Clock()


    def get_max_score(self):
        try:
            max_score = max(self.scores[self.name])
        except TypeError:
            max_score = 0
        except KeyError:
            max_score = 0
        return max_score



    def get_piece(self):
        return Piece(4, -2, random.choice(SHAPES))
    

    def is_valid_space(self):
        coords = self.get_coordinates()
        answer = True
        for block in coords:
            x = block[0]
            y = block[1]
            if block in self.filled_blocks:
                answer = False
            elif x < 0 or x > 9:
                answer = False
            elif y > 19:
                answer = False            
        return answer


    def remove_line(self, i, row):
        # Remove line from filled_blocks
        for j in range(len(row)):
            self.filled_blocks.pop((j, i))
        # Move filled blocks above the line down one level
        move_down = []        
        for x, y in [*self.filled_blocks]:
            if y < i:
                move_down.append((x, y))
        new_blocks = {}
        for x, y in move_down:
            new_blocks[(x, y+1)] = self.filled_blocks.pop((x, y))
        self.filled_blocks.update(new_blocks)
                
    
    def check_lost(self):
        answer = False
        for (x,y) in [*self.filled_blocks]:
            if y < 0:
                answer = True
        return answer

    
    def get_coordinates(self):
        return [ (self.current_piece.x + block[0], self.current_piece.y + block[1]) 
                   for block in self.current_piece.shape[self.current_piece.orientation] ]

       
    def lock_piece(self):
        coords = self.get_coordinates()
        color = self.current_piece.color
        for block in coords:
            self.filled_blocks[block] = color
        self.current_piece = self.next_piece
        self.next_piece = self.get_piece()
        
        # Check for lines to remove:
        remove_count = 0
        for i, row in enumerate(self.grid):
            remove = True
            if BACKGROUND in row:
                remove = False
            if remove:
                self.remove_line(i, row)
                remove_count += 1
        if remove_count:
            self.score += SCORE_REFERENCE[str(remove_count)]
        
        if self.check_lost():
            self.lose_game()
            
    
    def draw_grid_lines(self, window, grid):
        sx = TOP_LEFT_X
        sy = TOP_LEFT_Y
        
        for i in range(len(grid)):
            pygame.draw.line(window, LGRAY, (sx, sy + i*BLOCK_SIZE), (sx + GRID_PX_WIDTH, sy + i*BLOCK_SIZE))
            for j in range(len(grid[i])+1):
                pygame.draw.line(window, LGRAY, (sx + j*BLOCK_SIZE, sy), (sx + j*BLOCK_SIZE, sy + GRID_PX_HEIGHT))


    def make_grid(self):
        # Create blank grid
        grid = [[BACKGROUND for _ in range(10)] for _ in range(20)]
        # Fill in filled squares
        for j in range(len(grid)):
            for i in range(len(grid[j])):
                if (i, j) in self.filled_blocks:                    
                    grid[j][i] = self.filled_blocks[(i, j)]
        return grid


    def get_overall_max(self):
        overall_max = 0
        overall_name = ""
        for name, scores in self.scores.items():
            if max(scores) > overall_max:
                overall_max = max(scores)
                overall_name = name
        return overall_name, overall_max


    def draw_window(self):
        # Clear screen
        self.window.fill(BACKGROUND)
        # Draw header
        pygame.font.init()
        header_font = pygame.font.SysFont('comicsans', 50)
        header = header_font.render('Tetrisish', 1, PURPLE, BACKGROUND)
        self.window.blit(header, ((TOP_LEFT_X + GRID_PX_WIDTH // 2 - header.get_width() // 2), 10))
        # Draw next piece label
        next_font = pygame.font.SysFont('comicsans', 30)
        next_label = next_font.render('Next Piece', 1, GREEN, BACKGROUND)
        self.window.blit(next_label, (NEXT_TOP_LEFT_X - 20, NEXT_TOP_LEFT_Y - 50))
        # Draw name
        name_font = pygame.font.SysFont('comicsans', 20)
        name_label = name_font.render(f'Name: {self.name}', 1, YELLOW)
        self.window.blit(name_label, (TOP_LEFT_X - 140, TOP_LEFT_Y + 80))
        # Draw current score
        score_font = pygame.font.SysFont('comicsans', 30)
        score_label = score_font.render(f'Score: {self.score}', 1, BLUE)
        self.window.blit(score_label, (TOP_LEFT_X - 140, TOP_LEFT_Y + 130))
        # Draw your max score
        max_font = pygame.font.SysFont('comicsans', 20)
        max_label = max_font.render(f'Your max score:', 1, RED)
        max_label2 = max_font.render(f' {self.max_score}', 1, RED)
        self.window.blit(max_label, (TOP_LEFT_X - 145, TOP_LEFT_Y + 250))
        self.window.blit(max_label2, (TOP_LEFT_X - 145, TOP_LEFT_Y + 280))
        # Draw level
        level_font = pygame.font.SysFont('comicsans', 25)
        level_label = level_font.render(f'Level: {self.level}', 1, CYAN)
        self.window.blit(level_label, (TOP_LEFT_X + 340, TOP_LEFT_Y + 350))
        # Draw overall max score
        overall_name, overall_max = self.get_overall_max()
        overall_font = pygame.font.SysFont('comicsans', 20)
        overall_label = overall_font.render(f'Overall max score:', 1, ORANGE)
        overall_label2 = overall_font.render(f' {overall_max}', 1, ORANGE)
        held_font = pygame.font.SysFont('comicsans', 20)
        held_label = held_font.render(f'Held by: {overall_name}', 1, ORANGE)
        self.window.blit(overall_label, (TOP_LEFT_X - 145, TOP_LEFT_Y + 450))
        self.window.blit(held_label, (TOP_LEFT_X - 145, TOP_LEFT_Y + 510))
        self.window.blit(overall_label2, (TOP_LEFT_X - 145, TOP_LEFT_Y + 480))
        # Draw next_piece
        for block in self.next_piece.shape[0]:

            pygame.draw.rect(self.window, 
                             self.next_piece.color, 
                             (NEXT_TOP_LEFT_X + block[0]*BLOCK_SIZE, NEXT_TOP_LEFT_Y + block[1]*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 
                             0
                            )
        # Draw red outline
        pygame.draw.rect(self.window, RED, (TOP_LEFT_X, TOP_LEFT_Y, GRID_PX_WIDTH, GRID_PX_HEIGHT), 5)        
        # Draw the grid
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                pygame.draw.rect(self.window, 
                                 self.grid[i][j], 
                                 (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                                 0
                                )        
        # Draw grid lines
        self.draw_grid_lines(self.window, self.grid)
        # Update screen
        pygame.display.update()


    def lose_game(self):
        # Record the scores
        if self.name in self.scores.keys():
            self.scores[self.name].append(self.score)
        else:
            self.scores[self.name] = [self.score]
        self.save_scores()        
        # Check if player wants to play again or quit
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.play_again()
                    elif event.key == pygame.K_q:
                        self.terminate()                        

            pygame.draw.rect(self.window, WHITE, (150, 200, 350, 200), 0)

            game_over_font = pygame.font.SysFont('comicsans', 90)
            game_over_label = game_over_font.render('Game Over', 1, RED)
            self.window.blit(game_over_label, (150, 260))

            play_again_font = pygame.font.SysFont('comicsans', 30)
            play_again_label = play_again_font.render('Press Enter/Return to play again', 1, ORANGE)
            self.window.blit(play_again_label, (150, 310))

            quit_font = pygame.font.SysFont('commicsans', 30)
            quit_label = quit_font.render('Press "q" to quit', 1, ORANGE)
            self.window.blit(quit_label, (150, 340))

            self.clock.tick(15)
            pygame.display.update()

      
    def play_again(self):
        # Reset game state
        self.filled_blocks = {}
        self.scores = self.load_scores()
        self.max_score = max(self.scores[self.name])
        self.score = 0
        # Play again
        self.play()


    def terminate(self):        
        pygame.quit()
        sys.exit()


    def save_scores(self):
        with open(scores_PATH, 'w') as scores_file:
            scores_file.write(str(self.scores))

    
    def load_scores(self):
        try:
            with open(scores_PATH, 'r') as scores_file:
                return eval(scores_file.read())
        except FileNotFoundError:
            with open(scores_PATH, 'w') as file:
                file.write('{}')
            self.load_scores()

    
    def move_left(self):
        self.current_piece.x -= 1                  
        if not self.is_valid_space():
            self.current_piece.x += 1


    def move_right(self):
        self.current_piece.x += 1                     
        if not self.is_valid_space():
            self.current_piece.x -= 1


    def move_down(self):
        self.current_piece.y += 1
        if not self.is_valid_space():
            self.current_piece.y -= 1
            self.lock_piece()

    
    def play(self):
        # Initialize local variables
        fall_time = 0
        fall_speed = INIT_FALL_SPEED
        move_time = 0
        cycle_count = 0
        moving_down = False
        moving_left = False
        moving_right = False
        # Main game loop
        running = True
        while running:
            # Update times
            fall_time += self.clock.get_rawtime()
            move_time += self.clock.get_rawtime()
            # Check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.terminate()
                    elif event.key == pygame.K_RIGHT:
                        moving_right = True
                    elif event.key == pygame.K_LEFT:
                        moving_left = True
                    elif event.key == pygame.K_DOWN:
                        moving_down = True
                    elif event.key == pygame.K_UP:
                        # Change orientation of piece
                        self.current_piece.orientation = (self.current_piece.orientation + 1) % len(self.current_piece.shape)
                        if not self.is_valid_space():
                            self.current_piece.orientation = (self.current_piece.orientation -1) % len(self.current_piece.shape)
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        moving_down = False
                    elif event.key == pygame.K_LEFT:
                        moving_left = False
                    elif event.key == pygame.K_RIGHT:
                        moving_right = False             
            
            #Check for held down keys:
            if moving_down:
                if move_time/1000 > MOVE_SPEED:
                    self.move_down()
                    move_time = 0
            if moving_left:
                if move_time/1000 > MOVE_SPEED:
                    self.move_left()
                    move_time = 0
            elif moving_right:
                if move_time/1000 > MOVE_SPEED:
                    self.move_right()
                    move_time = 0
            # Put piece into grid
            self.grid = self.make_grid()
            if not self.is_valid_space():
                self.lose_game()            
            for block in self.current_piece.shape[self.current_piece.orientation]:
                x = self.current_piece.x + block[0]
                y = self.current_piece.y + block[1]
                if y > -1:
                    self.grid[y][x] = self.current_piece.color            
            # Check if piece needs to be dropped
            if fall_time/1000 > fall_speed:
                fall_time = 0
                self.move_down()            
            # Incriment cycle_count and check to raise level
            cycle_count += 1
            if cycle_count % CYCLES_TO_INCREASE_LEVEL == 0:
                self.level += 1
                fall_speed = INIT_FALL_SPEED * 0.75**self.level

            self.draw_window() 
            self.clock.tick()           


    def main_menu(self):
        # Get user name
        input_box = InputBox()
        self.name = input_box.ask(self.window, "Name (lowercase)")
        # Check if user has played before and find previous max score
        # if self.name in [*self.scores]:
        if self.name in self.scores.keys():
            self.max_score = max(self.scores[self.name])
        else:
            self.max_score = 0
        # Welcome screen, wait for user to press Enter/Return, then play game
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        running = False
                        self.play()

            self.window.fill(CYAN)

            header_font = pygame.font.SysFont('comicsans', 80)
            header_label = header_font.render('Welcome To Tetrisish', 1, PURPLE)
            self.window.blit(header_label, (15,100))

            greeting_font = pygame.font.SysFont('comicsans', 40)
            greeting_label = greeting_font.render(f'Hi {self.name}, your high score is {self.max_score}', 1, BLUE)
            self.window.blit(greeting_label, (60, 200))
            
            use_font = pygame.font.SysFont('comicsans', 30)
            use_label = use_font.render('Use the Up, Down, Left, and Right keys', 1, RED)
            self.window.blit(use_label, (60, 300))

            play_font = pygame.font.SysFont('comicsans', 30)
            play_label = play_font.render('Press Return/Enter to play', 1, RED)
            self.window.blit(play_label, (60, 400))

            pygame.display.update()
            self.clock.tick(15)


def main():
    game = Game()
    game.main_menu()


if __name__ == '__main__':
    main()

    
