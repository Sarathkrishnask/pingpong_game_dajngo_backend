import pygame
import os
import requests
import time
from tkinter import messagebox
# Initialize Pygame
pygame.init()

score_left = 0
score_right = 0

# Set up the screen
screen_width = 800
screen_height = 600
state=False
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Ping Pong Game")

# Set up colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE=(0, 0, 255)
YELLOW=(255, 255, 0)
ORANGE=(255, 165, 0)
PURPLE=(128, 0, 128)
PINK=(255, 192, 203)
CYAN=(0, 255, 255)
BROWN=(165, 42, 42)
GRAY=(128, 128, 128)

pad_clr=""
ball_clr=""
bg_clr=""
player_b=""
player_a=""

start_time=time.time()
def play_sound_async(file_name):
    """
    Play a sound asynchronously using pygame.

    Args:
    - file_name (str): The path to the sound file.
    """
    # Initialize the pygame mixer module
    pygame.mixer.init()

    # Load the sound file
    sound = pygame.mixer.Sound(os.path.join(os.getcwd(), "sounds", file_name))

    # Play the sound asynchronously
    sound.play(maxtime=0)

# Set up the Ball class
class Balls:
    # Initialize the ball object with color, radius, and speed attributes
    def __init__(self, color, radius, speed):
        self.color = color
        self.radius = radius
        # Set the initial position of the ball to the center of the screen
        self.x = screen_width // 2
        self.y = screen_height // 2
        # Set the initial speed of the ball in both x and y directions
        self.speed_x = speed
        self.speed_y = speed
        # Flag to track if the ball has scored in the current frame
        self.scored_this_frame = False
        self.score_=0

    # Method to change the color of the ball
    def chs_clr(self,clr):
        self.color = clr
    
    # Update the position of the ball based on its speed
    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        # Handle bouncing off the top and bottom boundaries
        if self.y - self.radius <= 0 or self.y + self.radius >= screen_height:
            self.speed_y *= -1
        # Handle bouncing off the left and right boundaries
        if self.x - self.radius <= 0 or self.x + self.radius >= screen_width:
            self.speed_x *= -1

    def draw(self):
        # Method to draw the ball on the screen
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def players(self,name_a,name_b):
        # Method to assign player names to the ball
        self.name_a = name_a
        self.name_b = name_b

    def set_score(self,max_data):
        self.score_=max_data
    
    def reset_position(self):
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.scored_this_frame = False  # Reset this flag if it's being used

    # def check_paddle_collision(self, paddle):
    #     # Method to check collision with a paddle
    #     global score_left, score_right,state,player_a,player_b
    #     if paddle.colliderect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2):
    #         # If collision occurs, reverse the horizontal speed of the ball
    #         play_sound_async("paddleballcol.wav")
    #         self.speed_x *= -1

    def check_paddle_collision(self, paddle):
        global score_left, score_right

        # Create a rectangle for the ball
        ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

        # Check for collision with the paddle
        if paddle.colliderect(ball_rect):
            # Find the center of the ball
            ball_center_x = self.x
            ball_center_y = self.y

            # Check where the ball hits the paddle and adjust accordingly
            if ball_center_x < paddle.left or ball_center_x > paddle.right:
                # The ball is hitting the paddle horizontally
                # Reverse the horizontal speed
                self.speed_x *= -1
                # Reposition the ball outside of the paddle
                if self.speed_x > 0:
                    # Ball is moving to the right; place it to the right of the paddle
                    self.x = paddle.right + self.radius
                else:
                    # Ball is moving to the left; place it to the left of the paddle
                    self.x = paddle.left - self.radius
            else:
                # The ball is hitting the paddle vertically
                # Reverse the vertical speed
                self.speed_y *= -1
                # Reposition the ball above or below the paddle
                if self.speed_y > 0:
                    # Ball is moving downwards; place it below the paddle
                    self.y = paddle.bottom + self.radius
                else:
                    # Ball is moving upwards; place it above the paddle
                    self.y = paddle.top - self.radius

            play_sound_async("paddleballcol.wav")

        else:
            # Update score if the ball passes the paddle and scores a point 
            if self.x - self.radius <= 0 and not self.score_updated:
                play_sound_async("paddleballcol.wav")
                self.score_updated = True
                score_right += 1
                # if score_right==self.score_:
                #     play_sound_async("playerawins.wav")

            elif self.x + self.radius >= screen_width and not self.score_updated:
                play_sound_async("paddleballcol.wav")
                self.score_updated = True
                score_left += 1
                # if score_left==self.score_:
                #     play_sound_async("playerawins.wav")

            # Reset score_updated flag when ball is not colliding with the boundary
            if self.x - self.radius > 0 and self.x + self.radius < screen_width:
                self.score_updated = False


# Set up the paddles
paddle_width = 20
paddle_height = 80

#setup the position of each paddle and paddle l x b
left_paddle = pygame.Rect(5, screen_height // 2 - paddle_height // 2, paddle_width, paddle_height)
right_paddle = pygame.Rect(screen_width - 5 - paddle_width, screen_height // 2 - paddle_height // 2, paddle_width, paddle_height)

# Set up the main game loop
clock = pygame.time.Clock()
running = True

# Create two balls using the Ball class
ball1 = Balls(RED, 10, 3)
ball2 = Balls(GREEN, 10, 2)

# Paddle speed
paddle_speed = 5
game_started=False
play_sound_async("gamesound.wav")
# Main loop
def start(pad_clr,ball_clr,bg_clr,player_a,player_b,max_score):
    
    global running, game_started, score_left, score_right
    ball1.chs_clr(GREEN)
    ball2.chs_clr(RED)
    running = True
    while running:
        #to save the color into varianle
        pd = pad_clr.upper()
        bal_clr = ball_clr.upper()
        b_clr = bg_clr.upper()
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    game_started = True

        if game_started:
            # Move paddles based on key presses
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and right_paddle.top > 0:
                right_paddle.y -= paddle_speed
            if keys[pygame.K_DOWN] and right_paddle.bottom < screen_height:
                right_paddle.y += paddle_speed
            if keys[pygame.K_w] and left_paddle.top > 0:
                left_paddle.y -= paddle_speed
            if keys[pygame.K_s] and left_paddle.bottom < screen_height:
                left_paddle.y += paddle_speed

        # Move the balls
        if game_started:
            ball1.move()
            ball2.move()

        # Check collisions with paddles
        if game_started:
            ball1.check_paddle_collision(left_paddle)
            ball1.check_paddle_collision(right_paddle)
            ball2.check_paddle_collision(left_paddle)
            ball2.check_paddle_collision(right_paddle)

        # Clear the screen
        screen.fill(b_clr)

        # Draw the paddles and setup the colors
        if game_started:
            pygame.draw.rect(screen, pd, left_paddle)
            pygame.draw.rect(screen, pd, right_paddle)

        # Draw the balls
        if game_started:
            ball1.draw()
            ball2.draw()

        # Draw score
        font = pygame.font.Font(None, 36)
        score_display = font.render(f"{player_a}:{score_left} - {player_b}:{score_right}", True, WHITE)
        screen.blit(score_display, (screen_width // 2 - score_display.get_width() // 2, 20))

        #check the scrore point and post the data to api endpoint
        if score_left >= int(max_score) or score_right >= int(max_score):
            winner = player_a if score_left >= int(max_score) else player_b
            win_msg = font.render(f"{winner} wins!", True, WHITE)
            screen.blit(win_msg, (screen_width // 2 - win_msg.get_width() // 2, screen_height // 2))
            pygame.display.flip()  # Update the display to show the winner
            play_sound_async("playerawins.wav")
            pygame.time.wait(3000)  # Wait for 3 seconds before breaking out of the loop
            elapsed_time = time.time()-start_time
            datas = {
    
                "playername":{"player_a": player_a, "player_b": player_b},
                "whichgame": str("2_ball_game"),
                "timeplayed":str(elapsed_time),
                "player_won":str(winner)
            }
            #post the data to API endpoint to save the data to db
            response = requests.post("http://127.0.0.1:8000/account/playerdata/",json = datas)
            # Ask the player if they want to play again
            response = messagebox.askyesno("New Game", "Play Again?")
            if response: # If the player wants to play again
                ball1.reset_position()
                ball2.reset_position()
                score_left = 0
                score_right = 0
                game_started = False
                continue
            else:
                break
                # break  # Exit the loop

        # Start message
        if not game_started:
            ball1.players(player_a,player_b)
            ball1.chs_clr(bal_clr)
            ball2.chs_clr(bal_clr)
            ball1.set_score(max_score)
            ball2.set_score(max_score)
            start_msg = font.render("Press 'S' to start the game", True, WHITE)
            screen.blit(start_msg, (screen_width // 2 - start_msg.get_width() // 2, screen_height // 2))
            

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    # Quit Pygame
    pygame.quit()

