import turtle
import time
import random
from tkinter import messagebox
from tkinter import simpledialog
import os
import csv
import pygame
import tkinter as tk
import requests
import json

# Initialize the turtle window
window = turtle.Screen()
window.title("Ping-Pong")
window.bgcolor("black")
window.setup(width=800, height=600)
window.tracer(0)  # Delays drawing update on canvas

# Initial velocities for the ball
xVelocity = 3.40
yVelocity = 2.40
selected_color=""

start_time = time.time()
# Player data list
player_data = []
# Initialize objects

# File path for player data
player_data_file = os.path.join(os.path.expanduser("~"), "Downloads", "player_data.csv")

# Initialize power-up variable
power = None

player_a_name =""
player_b_name = "computer"  # Default opponent name
player_a_score = player_b_score = 0


def difficulty_level():
    levels = ["easy", "medium", "hard"]
    difficulty = simpledialog.askstring("Difficulty?", "Choose a difficulty level (easy/medium/hard): ")
    while difficulty.lower() not in levels:
        difficulty = simpledialog.askstring("Difficulty?", "Choose a difficulty level (easy/medium/hard): ")
    return difficulty.lower()


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

def create_welcome_window():
    # Create a new Tkinter window
    root=tk.Tk()

    # Define a function to open the login window
    def open_login_window():
        # Destroy all widgets in the root window
        for widget in root.winfo_children():
            widget.destroy()
        # Call the user_login function to create the login window
        user_login()
        # Destroy the root window after opening the login window
        root.destroy()

    # Define a function to open the register window
    def open_register_window():
        # Destroy all widgets in the root window
        for widget in root.winfo_children():
            widget.destroy()
        # Call the create_registration_form function to create the registration form window
        create_registration_form()
        # Destroy the root window after opening the registration form window
        root.destroy()

    # Create "Login" button
    # Set window attributes and position it in the center of the screen
    root.attributes("-toolwindow", True)  # Remove maximize icon
    window_width = 150
    window_height = 100
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)
    root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))

    # Create "Login" button and pack it into the window
    login_button = tk.Button(root, text="Login", width=10,
                              command=open_login_window)
    login_button.pack(padx=20, pady=(20, 10))

    # Create "Register" button and pack it into the window
    register_button = tk.Button(root, text="Register", width=10,
                                 command=open_register_window)
    register_button.pack(pady=10)
    
    # Enter the Tkinter event loop
    root.mainloop()
    


# Function to write player data to CSV file
def write_player_data(player_data_file):
    print("=============")
    with open(player_data_file, "a", newline="") as file:
        csv_writer = csv.DictWriter(file, fieldnames=["Player Name", "Difficulty"])

        # Check if the file is empty
        if file.tell() == 0:
            # If the file is empty, write the header row
            csv_writer.writeheader()
        # Write a row to the CSV file with player name and difficulty
        csv_writer.writerow({"Player Name": player_a_name, "Difficulty": difficulty})

# Function to read player data from CSV file
def read_player_data():

    global player_a_name, difficulty, player_data, player_data_file

    # Check if the player data file exists  
    if not os.path.isfile(player_data_file):
        # If the file doesn't exist, show an error message
        messagebox.showerror("File Not Found", "Player Data Missing!")

        # Provide a default file path for the player data file
        player_data_file = os.path.join(os.path.expanduser("~"), "Downloads", "player_data.csv")

        # Ask the user to enter a player name
        player_a_name = simpledialog.askstring("Name?", "please enter a player name if you have one: ")
        # Add the player's name and difficulty to the player_data list as a dictionary
        player_data.append({"Player Name": player_a_name, "Difficulty": difficulty})
        return
    
    with open(player_data_file, "r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            player_data.append({"Player Name": row["Player Name"], "Difficulty": row["Difficulty"]})

# Function to prompt for a new player
def new_player():

    newplayer = messagebox.askyesno("New Player?", "new (Yes) or same player? (No)")
    return newplayer

# Function to reset the game
def reset_game():
  
    if not new_game():
        window.bye()



class SPaddle(turtle.Turtle): #passing a turtle.Turtle object as a superclass
    global selected_color
    print("color :", selected_color)
    def __init__(self,x,y,selected_color):
    
        super().__init__() #ensures the paddle object inherits turtle.Turtle's attributes
        self.shape("square") # Set the shape of the paddle to square
        self.shapesize(stretch_wid=5, stretch_len=1) # Set the size of the paddle
        self.color(str(selected_color)) # Set the color of the paddle
        self.penup() # Lift the pen up to avoid drawing lines when moving
        self.speed(0) # Set the speed of the paddle's animation to maximum  
        self.goto(x, y) # Move the paddle to the specified coordinates

    # Method to change the color of the paddle 
    def ask_clr(self,clr):
        self.color(clr)
        
    # Method to move the paddle up
    def paddle_up(self):
        self.sety(self.ycor() + 10)

    # Method to move the paddle down
    def paddle_down(self):
        self.sety(self.ycor() - 10)
    
    
    # AI paddle using ball's ycor to determine movement
    def ai_paddle(self,ball, difficulty):
        global xVelocity, yVelocity
         # Determine the threshold for paddle movement based on difficulty
        if difficulty == "easy":
            threshold = 0.1

        elif difficulty == "medium":
            threshold = 0.2

        elif difficulty == "hard":
            threshold = 0.3

        # Move the paddle towards the ball's y-coordinate with probability determined by threshold
        if random.random() < threshold:
            if self.ycor() < ball.ycor():
                self.sety(self.ycor() + 0.5 * (ball.ycor() - self.ycor()))

            else:
                self.sety(self.ycor() - 0.5 * (self.ycor() - ball.ycor()))


    # Check if paddle hits borders
    def check_border(self):
        if self.ycor() > 248:
            self.sety(248)
        elif self.ycor() < -248:
            self.sety(-248)

# Ball class
class Ball(turtle.Turtle):
    def __init__(self, x, y):
        super().__init__()
        self.shape("circle") # set the shape of ball 
        self.penup() # Lift the pen up to avoid drawing lines when moving
        self.speed(0) # set the speed of ball initially to zero
        self.goto(x, y) # initial position of ball 
        self.x=0
        self.y=0

    #To change the ball color by user interest
    def change_clr(self,clr):
        self.color(clr)

    # Move the ball
    def move_ball(self):
        self.setx(self.xcor() + 0.1 * xVelocity)
        self.sety(self.ycor() + 0.1 * yVelocity)

    # Check if ball hits borders
    def border_checking(self):
        global xVelocity, yVelocity, player_a_score, player_b_score

        # Right border
        if self.xcor() > 390:
            self.setx(390) #border x-limit 
            xVelocity *= -1 #change the velocity once hit border
            player_a_score += 1 #update the score value
            play_sound_async("score.wav") #play background sound 
            score.clear() #clear the previous score and update new score
            #Update the score values in display for player and their scores
            score.write("{}:{} | {}:{}".format(player_a_name, player_a_score, player_b_name, player_b_score), align="center", font=("Consolas", 15, "normal"))

        # Left border
        if self.xcor() < -390:
            self.setx(-390) #border x-limit 
            xVelocity *= -1 #change the velocity once hit border
            player_b_score += 1 #update the score value
            play_sound_async("score.wav") #play background sound 
            
        #top border
        if self.ycor() > 290:
            self.sety(290) #border y-limit 
            yVelocity *= -1 #change the velocity once hit border

        #lower border
        if self.ycor() < -290:
            self.sety(-290) #border y-limit 
            yVelocity *= -1 #change the velocity once hit border
        

    def collisions(self):
        global xVelocity, yVelocity, power

        if self.color()[0] == "red":
            # Handle collision with power-up ball
            if (350 > self.xcor() > 340) and (paddle_b.ycor() + 40 > self.ycor() > paddle_b.ycor() - 40):
                self.setx(340)
                xVelocity *= -1
                play_sound_async("paddleballcol.wav")
            
            elif (-350 < self.xcor() < -340) and (paddle_a.ycor() - 40 < self.ycor() < paddle_a.ycor() + 40):
                self.setx(-340)
                xVelocity *= -1
                play_sound_async("paddleballcol.wav")

        else:
            # Regular collision detection
            if (350 > self.xcor() > 340) and (paddle_b.ycor() + 40 > self.ycor() > paddle_b.ycor() - 40):
                self.setx(340)
                xVelocity *= -1
                play_sound_async("paddleballcol.wav")
            
            elif (-350 < self.xcor() < -340) and (paddle_a.ycor() - 40 < self.ycor() < paddle_a.ycor() + 40):
                self.setx(-340)
                xVelocity *= -1
                play_sound_async("paddleballcol.wav")

            if power is not None and self.distance(power) <= 20:
                play_sound_async("powerballcol.wav")
                power.hideturtle()
                self.color("red")
                power = None
                xVelocity *= -1
                yVelocity *= -1


# Score class
class Score(turtle.Turtle):
    def __init__(self, x, y):
        super().__init__()
        self.color("white") # here we set the color of font 
        self.penup()# Lift the pen up to avoid drawing lines when moving
        self.speed(0) # set the initial speed
        self.goto(x,y) # Move the display to the specified coordinates (x, y)
        self.hideturtle() # Hide the turtle cursor (display) from the screen
        #Update the score values in display for player and their scores
        self.write("{}:{} | {}:{}".format(player_a_name, player_a_score, player_b_name, player_b_score), align="center", font=("Consolas", 15, "normal"))


# Display class
class Display(turtle.Turtle):
    def __init__(self, x, y):
        super().__init__()
        self.color("white") # here we set the color of font 
        self.penup() # Lift the pen up to avoid drawing lines when moving
        self.speed(0) # set the initial speed of animation
        self.goto(x, y) # Move the display to the specified coordinates (x, y)
        self.hideturtle() # Hide the turtle cursor (display) from the screen
        # Below code will show the usage of keys and it will show in display
        self.write("Press 's' to start\nQuit: q | Move Up: \u2191 | Move Down: \u2193\nAvoid the power up ball :D", align="center", font=("Consolas", 15, "normal"))
    

# Winner class
class Winner(turtle.Turtle):
    def __init__(self, x, y):
        super().__init__()
        self.color("white")  # here we set the color of font 
        self.penup() # Lift the pen up to avoid drawing lines when moving
        self.speed(0) # set the initial speed of animation
        self.goto(x, y) # Move the display to the specified coordinates (x, y)
        self.hideturtle() # Hide the turtle cursor (display) from the screen

# Power-up class
class Powerup(turtle.Turtle):
    def __init__(self, x, y):
        super().__init__()
        self.shape("circle") # we set the powerup ball shape
        self.color("red") # we choose the color of ball is to be red color
        self.penup() # Lift the pen up to avoid drawing lines when moving
        self.speed(0) #set the speed initial zero
        self.goto(x, y) #set the position of coordates
        self.hideturtle() #Hide the turtle cursor from screen

    # Show power-up
    def show_powerup(self):
        self.showturtle()

    # Hide power-up
    def hide_powerup(self):
        self.hideturtle()

# Function to handle game over
def game_over():
    global winner, xVelocity, yVelocity,player_,score_lvl
    if player_a_score == int(score_lvl):
        player_= player_a_name
        ball.goto(0,0)
        play_sound_async("playerawins.wav")
        winner.write("{} wins!👏🏽".format(player_a_name), align="center", font=("Consolas", 14, "normal"))
        window.update()
        time.sleep(1.1)
        winner.clear()
        global game_type
        datas = {
        
            "playername":{"player_a": player_a_name, "player_b": player_b_name},
            "whichgame": str(game_type),
            "timeplayed":str(elapsed_time),
            "player_won":str(player_)
        }

        response = requests.post("http://127.0.0.1:8000/account/playerdata/",json = datas)
        return True   

    elif player_b_score == int(score_lvl):
        player_= player_b_name
        ball.goto(0,0)
        play_sound_async("playerbwins.wav")
        winner.write("{} wins!👏🏽".format(player_b_name), align="center", font=("Consolas", 14, "normal"))
        window.update()
        time.sleep(1.1)
        winner.clear()
         
        datas = {
        
            "playername":{"player_a": player_a_name, "player_b": player_b_name},
            "whichgame": str(game_type),
            "timeplayed":str(elapsed_time),
            "player_won":str(player_)
        }

        response = requests.post("http://127.0.0.1:8000/account/playerdata/",json = datas)
        # if response.status_code==200:
        return True
    else:
        return False
    
# Function to start a new game
def new_game():
    
    global player_a_name, player_data_file, player_data, display, paddle_a, paddle_b, player_a_score, player_b_score, power, start_time, xVelocity, yVelocity

    # Ask the player if they want to play again
    response = messagebox.askyesno("New Game", "Play Again?")
    if response: # If the player wants to play again

        # Reset global variables and game elements
        newplayer = new_player() # Check if it's a new player
        if newplayer:

            # If it's a new player, prompt for their name and difficulty level
            player_a_name = simpledialog.askstring("Name?", "please enter a player name if you have one: ")
            difficulty = difficulty_level()
            display.write("Press 's' to start\nQuit: q | Move Up: ↑ | Move Down: ↓\nAvoid the power up ball :D", align="center", font=("Consolas", 15, "normal"))
            play_sound_async("gamesound.wav")# Play game sound asynchronously
            
            window.listen() # Listen for keypress events
            window.onkeypress(start_game, "s")# Start the game on keypress 's'
        else:
            # If it's not a new player, ask if they want to change difficulty level
            change_difficulty = messagebox.askyesno("New Difficulty?", "change difficulty level? ")
            if change_difficulty:
                difficulty = difficulty_level()# Prompt for new difficulty level
                display.write("Press 's' to start\nQuit: q | Move Up: ↑ | Move Down: ↓\nAvoid the power up ball :D", align="center", font=("Consolas", 15, "normal"))
                play_sound_async("gamesound.wav") # Play game sound asynchronously
                
            else:
                read_player_data() # Read player data from file
                display.write("Press 's' to start\nQuit: q | Move Up: ↑ | Move Down: ↓\nAvoid the power up ball :D", align="center", font=("Consolas", 15, "normal"))
                play_sound_async("gamesound.wav") # Play game sound asynchronously
                
        # Reset player scores and display them
        player_a_score = player_b_score = 0
        winner.clear()
        score.clear()
        score.write("{}:{} | {}:{}".format(player_a_name, player_a_score, player_b_name, player_b_score), align="center", font=("Consolas", 15, "normal"))

        # Reset paddle and ball positions
        paddle_a.goto(-350,0)
        paddle_b.goto(350,0)
        ball.goto(0,0)
        ball.hideturtle()
        paddle_a.hideturtle()
        paddle_b.hideturtle()

        # Reset the time
        start_time = time.time()

        # Hide the power-up ball if it exists
        if power is not None:
            power.hide_powerup()

        #Reset ball velocity
        xVelocity = 4
        yVelocity = 3
        ball.move_ball()

        powerup_timer()

        # Write player data to file
        write_player_data(player_data_file)

            
        window.update() # Update the game window
        window.mainloop() # Enter the main event loop

    else: # If the player doesn't want to play again
        window.bye()

# Function to manage power-up appearance
def powerup_timer():
    global power, start_time, xVelocity, yVelocity , elapsed_time

    # Calculate the elapsed time since the start of the game
    elapsed_time = time.time() - start_time
    # Activate power-up after 30 seconds if no power-up is active and the ball is not red
    if elapsed_time > 30 and power is None and ball.color()[0] != "red":

        # Generate and show a new power-up at random position
        power = Powerup(x=random.randint(-340, 340), y=random.randint(-250, 250))
        power.show_powerup()
        play_sound_async("powerup.wav") # Play power-up sound asynchronously
        # Increase ball velocity by 10% for both x and y directions
        xVelocity *= 1.1
        yVelocity *= 1.1
        start_time = time.time()  #Reset the start time for power-up duration

    powerup_elapsed_time = time.time() - start_time

    # Check if the duration of the active power-up has exceeded 18 seconds
    if powerup_elapsed_time > 18 and power is not None:
        # Hide the power-up and reset power-up variables
        power.hide_powerup()
        power = None
        start_time = time.time() # Reset the start time for next power-up activation


def update_score():
    score.clear() # Here we just clear the old score and update
    # update the score once player loss
    score.write("{}:{} | {}:{}".format(player_a_name, player_a_score, player_b_name, player_b_score), align="center", font=("Consolas", 15, "normal"))


def start_game():
    print('---------------------------')
    global display ,state, paddle_a, paddle_b,ball, score,winner
    
    while True: # Enter an infinite loop for continuous gameplay
        window.update() # Update the game window
        display.clear() # Clear the display for updating game information

        # Show the ball, move it, check borders, and handle collisions
        ball.showturtle()
        ball.move_ball()
        ball.border_checking()
        ball.collisions()
        
        # Depending on the game state, show and control paddles
        if state == True: # If the game is in play state
            paddle_a.showturtle()
            paddle_b.showturtle()
            paddle_a.check_border()
            paddle_b.check_border()
            paddle_b.ai_paddle(ball, difficulty) # Control AI paddle's movement
        else: # If the game is not in play state
            paddle_a.showturtle()
            paddle_b.showturtle()
            paddle_a.check_border()
            paddle_b.check_border()
       
        powerup_timer() # Manage power-up activation and duration
        update_score() # Update the score displayed on the screen

        if game_over(): #check game is over ?
            new_game() # Start a new game if the current game is over

def set_names():
    # Define a nested function to handle form submission
    def submit():
        # Get the form data
        global first_, second_, player_a_name, player_b_name
        first_ = first_player_entry.get()
        second_ = sec_player_entry.get()

        # Validate the form data
        if not first_ or not second_:
            tk.messagebox.showerror("Error", "Please fill in all fields.")
            return
        # Assign player names and close the form window
        player_a_name = first_
        player_b_name = second_
        root.destroy()
        ask_difficult()

    # Create the Tkinter window for the form
    # Set window attributes and position it in the center of the screen
    root = tk.Tk()
    root.title("name Form")
    root.attributes("-toolwindow", True)  # Remove maximize icon
    window_width = 200
    window_height = 100
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)
    root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))

    # Create form elements: labels, entry fields, and submit button
    first_player_label = tk.Label(root, text="First:")
    first_player_entry = tk.Entry(root)
    sec_player_label = tk.Label(root, text="Second:")
    sec_player_entry = tk.Entry(root)

    # Create the submit button
    submit_button = tk.Button(root, text="Set Names", command=submit)

    # Place the form fields on the screen
    first_player_label.grid(row=0, column=0)
    first_player_entry.grid(row=0, column=1)

    sec_player_label.grid(row=1, column=0)
    sec_player_entry.grid(row=1, column=1)

    submit_button.grid(row=2, column=1)

def ask_difficult():
    global xVelocity,yVelocity,difficulty,paddle_a,paddle_b
    # Prompt the user to select a difficulty level
    difficulty=difficulty_level()    
    # Set ball velocity based on the chosen difficulty level
    if difficulty == "easy":
        xVelocity=1
        yVelocity=1
    if difficulty == "medium":
        xVelocity=2 
        yVelocity=2
    if difficulty == "hard":
        xVelocity=3
        yVelocity=3

def s_player():
    # Ask for difficulty level
    ask_difficult()
    # Set global variables
    global state ,game_type
    state = True # Set game state to True (indicating the game is in progress)
    game_type = "single" # Set game type to single-player

    # Listen for keypress events
    window.listen()

    # Set colors and controls
    paddle_a.ask_clr(selected_color) # Set paddle color
    paddle_b.ask_clr(selected_color) # Set paddle color
    ball.change_clr(selected_ball_color) # Set ball color
    window.bgcolor(selected_background_color) # Set background color
    window.onkeypress(paddle_a.paddle_up, "Up") # Bind paddle movement to Up arrow key 
    window.onkeypress(paddle_a.paddle_down, "Down") # Bind paddle movement to Down arrow key    
    window.onkeypress(reset_game, "q") # Bind game reset to 'q' key
    window.onkeypress(start_game, "s") # Bind game start to 's' key
    window.mainloop()

def d_player():
    #Below function will calls the set name fucntion to set player names
    set_names()

    global state ,game_type
    state = False # Set game state to False (indicating the game is in progress)
    game_type = "double" # Set game type to double-player
    # Listen for keypress events
    window.listen()
    # Set colors and controls
    paddle_a.ask_clr(selected_color)# Set paddle color
    paddle_b.ask_clr(selected_color)# Set paddle color
    ball.change_clr(selected_ball_color) #set ball color
    window.bgcolor(selected_background_color) # Set background color
    window.onkeypress(paddle_a.paddle_up, "Up") # Bind paddle movement to Up arrow key 
    window.onkeypress(paddle_a.paddle_down, "Down") # Bind paddle movement to Down arrow key 
    window.onkeypress(paddle_b.paddle_up, "w") # Bind paddle movement to W  key 
    window.onkeypress(paddle_b.paddle_down, "e") # Bind paddle movement to E  key  
    window.onkeypress(reset_game, "q") # Bind game reset to 'q' key
    window.onkeypress(start_game, "s")# Bind game start to 's' key
    window.mainloop()


def game_mode():
    def normal_mode():
        root.destroy()  # Close the current window
        which_game() # Proceed to the next step (choosing game difficulty)

    def multi_ball():
        root.destroy()  # Close the current window
        pygame.mixer.stop() #stop all background music
        pygame.mixer.quit()
        window.bye() # Close the game window
        
        advance_lvl() # Proceed to the next step (multi-ball mode)

    def rapid():
        root.destroy()  # Close the current window
        pygame.mixer.stop() #stop all background music
        pygame.mixer.quit()
        window.bye() #close the current window
        rapid_fire() # Proceed to the next step (rapid fire mode)

    # Set window attributes and position it in the center of the screen
    root = tk.Tk()
    root.title("Choose Game Mode")
    root.attributes("-toolwindow", True)  # Remove maximize icon
    window_width = 150
    window_height = 150
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)
    root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))

    # Create buttons for each game mode
    single = tk.Button(root, text="Normal Mode", width=20, command=normal_mode)
    single.pack(pady=(20, 10)) # Adjust vertical padding between buttons

    double = tk.Button(root, text="2 ball mode", width=20, command=multi_ball)
    double.pack(pady=10) # Adjust vertical padding between buttons

    double = tk.Button(root, text="Rapid mode", width=20, command=rapid)
    double.pack(pady=10) # Adjust vertical padding between buttons

    root.mainloop() # Enter the Tkinter event loop

def advance_lvl():
    global selected_color,selected_ball_color,selected_background_color,score_lvl
    # Import the 'mutli_ba' module
    import multi_ball as multi_ball
    # Start the game with selected options
    multi_ball.start(selected_color,selected_ball_color,selected_background_color,player_a_name,player_b_name,score_lvl)

def rapid_fire():
    global selected_color,selected_ball_color,selected_background_color,score_lvl
    # Import the 'rapid' module
    import rapid as rapid
    # Start the game with selected options
    rapid.start(selected_color,selected_ball_color,selected_background_color,player_a_name,player_b_name,score_lvl)

    
def which_game():
    # Define function for single-player mode
    def single_player():
        root.destroy()  # Close the current window
        s_player()  # Start single-player game mode

    # Define function for double-player mode
    def double_player():
        root.destroy()  # Close the current window
        d_player()  # Start double-player game mode

    # Set window attributes and position it in the center of the screen
    root = tk.Tk()
    root.title("Choose Game Mode")
    root.attributes("-toolwindow", True)  # Remove maximize icon
    window_width = 150
    window_height = 100
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)
    root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))

    # Create buttons for single-player and multiplayer modes
    single = tk.Button(root, text="Single Player", width=20, command=single_player)
    single.pack(pady=(20, 10)) # Adjust vertical padding between buttons

    double = tk.Button(root, text="Multiplayer", width=20, command=double_player)
    double.pack(pady=10)# Adjust vertical padding between buttons

    root.mainloop() # run the event loop of tkinter

def set_max_score():
    
    # Define the submit function for the login form
    def submit():
        # Import global variables
        global score_lvl
        # Get the form data
        score_lvl = max_score.get()
        # print(score_lvl)
        # Clear the form fields
        max_score.delete(0, tk.END)
        # Close the color selection window
        root.destroy()
        # Proceed to choose the game mode
        game_mode()

    # Create a new Tkinter window for the login form and align it center
    root = tk.Tk()
    root.title("Set Max Score")
    root.attributes("-toolwindow", True)  # Remove maximize icon
    window_width = 200
    window_height = 100
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)
    root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))

    # Create labels and entry fields for email and password
    score_lvl = tk.Label(root, text="score:")
    max_score = tk.Entry(root)

    # Create the submit button
    submit_button = tk.Button(root, text="set score", command=submit)

    # Place the form fields on the screen
    score_lvl.grid(row=0, column=0)
    max_score.grid(row=0, column=1)
    submit_button.grid(row=2, column=1)

    

def choose_clr():
    # Retrieve selected colors from the radio buttons
    global selected_color, selected_background_color, selected_ball_color
    def submit_color():
        global selected_color, selected_background_color, selected_ball_color
        selected_color = color_var.get()
        selected_background_color = background_color_var.get()
        selected_ball_color = ball_color_var.get()

        # Check if all three colors are the same
        if selected_color == selected_background_color == selected_ball_color:
            messagebox.showwarning("Warning", "Paddle color, background color, and ball color are the same. Please choose different colors.")
            choose_clr()  # Reopen the color selection window
            return

        if selected_background_color == selected_ball_color:
            messagebox.showwarning("Warning", "background color, and ball color are the same. Please choose different colors.")
            choose_clr()  # Reopen the color selection window
            return
        if selected_color == selected_background_color:
            messagebox.showwarning("Warning", "Paddle color, background color are the same. Please choose different colors.")
            choose_clr()  # Reopen the color selection window
            return
        
        root.destroy()
        set_max_score()
    

    # Set window attributes and position it in the center of the screen
    root = tk.Toplevel()
    root.title("Choose Colors")
    root.attributes("-toolwindow", True)  # Remove maximize icon
    window_width = 400
    window_height = 350
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)
    root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))
    colors = [
        ("Red", "red"),
        ("Green", "green"),
        ("Blue", "blue"),
        ("Yellow", "yellow"),
        ("Orange", "orange"),
        ("Purple", "purple"),
        ("Pink", "pink"),
        ("Cyan", "cyan"),
        ("Brown", "brown"),
        ("Gray", "gray"),
    ]
    # Initialize Tkinter StringVars for color selection
    color_var = tk.StringVar()
    background_color_var = tk.StringVar()
    ball_color_var = tk.StringVar()
    background_color_var.set(None)
    color_var.set(None)
    ball_color_var.set(None)
    # Create frames for each color selection category
    color_frame = tk.Frame(root)
    background_color_frame = tk.Frame(root)
    ball_color_frame = tk.Frame(root)

    color_frame.pack(side=tk.LEFT, padx=10)
    background_color_frame.pack(side=tk.LEFT, padx=10)
    ball_color_frame.pack(side=tk.LEFT, padx=10)

    # Create radio buttons for selecting colors
    tk.Label(color_frame, text="Select Paddle Color:").pack()
    tk.Label(background_color_frame, text="Select Background Color:").pack()
    tk.Label(ball_color_frame, text="Select Ball Color:").pack()
    # Add radio buttons for each color option
    for color_name, color_value in colors:
        tk.Radiobutton(color_frame, text=color_name, variable=color_var, value=color_value).pack(anchor=tk.W)
        tk.Radiobutton(background_color_frame, text=color_name, variable=background_color_var, value=color_value).pack(anchor=tk.W)
        tk.Radiobutton(ball_color_frame, text=color_name, variable=ball_color_var, value=color_value).pack(anchor=tk.W)
    # Create a button to submit color selections
    submit_button = tk.Button(root, text="Submit", command=submit_color)
    submit_button.pack()
    submit_button.place(relx=0.5, rely=1.0, anchor=tk.S)

    root.mainloop() #Enter the Tkiner event loop

def user_login():
    # Import global variables
    global paddle_b,paddle_a
    # Define the submit function for the login form
    def submit():
        # Get the form data
        email = email_entry.get()
        password = password_entry.get()
   
        # Validate the form data
        if not  email or not password:
            tk.messagebox.showerror("Error", "Please fill in all fields.")
            return

        # Create a dictionary with the form data
        datas = {
      
            # "email":email,
            # "password": password
            "email":"viji@gmail.com",
            "password": "viji"
        }
        # Send a POST request to the login API endpoint
        response = requests.post("http://127.0.0.1:8000/account/AdminLoginApi/",json = datas)

        # Clear the form fields
        email_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

        # Handle the response
        if response.status_code == 200:
            # Extract user information from the response
            global player_a_name, player_b_name, difficulty
            response_data = response.json()
            player_a_name = response_data['result']['data']['user_info']['name']
            
            # Close the login window
            root.destroy()
            # Play the sound asynchronously
            play_sound_async("gamesound.wav")

            # Proceed to choose colors for the game
            choose_clr()
            root.destroy()


    # Create a new Tkinter window for the login form and align it center
    root = tk.Tk()
    root.title("Login Form")
    root.attributes("-toolwindow", True)  # Remove maximize icon
    window_width = 200
    window_height = 100
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)
    root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))

    # Create labels and entry fields for email and password
    email_label = tk.Label(root, text="Email:")
    email_entry = tk.Entry(root)

    password_label = tk.Label(root, text="Password:")
    password_entry = tk.Entry(root, show="*")

    # Create the submit button
    submit_button = tk.Button(root, text="Login", command=submit)

    # Place the form fields on the screen
    email_label.grid(row=0, column=0)
    email_entry.grid(row=0, column=1)
    password_label.grid(row=1, column=0)
    password_entry.grid(row=1, column=1)
    submit_button.grid(row=2, column=1)


def create_registration_form():
    def submit():
        # Get the form data
        name = name_entry.get()
        email = email_entry.get()
        password = password_entry.get()
        phone_number = phone_number_entry.get()

        # Validate the form data
        if not name or not email or not password:
            tk.messagebox.showerror("Error", "Please fill in all fields.")
            return

        # Create a dictionary with the form data
        datas = {
            "firstname":name,
            "email":email,
            "phone_number": phone_number,
            "password": password
        }
        # Send a POST request to the login API endpoint
        response = requests.post("http://127.0.0.1:8000/account/registeruser/",json = datas)

        # Clear the form fields
        name_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

        if response.status_code == 201:
            # Extract user information from the response
            root.destroy() #destroy the window
            user_login() #calls the user login fucntion for user need to login 

    # Create a new Tkinter window for the login form and align it center
    root = tk.Tk()
    root.title("Registration Form")
    root.attributes("-toolwindow", True)  # Remove maximize icon
    window_width = 300
    window_height = 150
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)
    root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))

    # Create labels and entry fields for email,name,phonenumber and password
    name_label = tk.Label(root, text="Name:")
    name_entry = tk.Entry(root)

    email_label = tk.Label(root, text="Email:")
    email_entry = tk.Entry(root)

    password_label = tk.Label(root, text="Password:")
    password_entry = tk.Entry(root, show="*")

    phone_number_label = tk.Label(root, text="Phone Number:")
    phone_number_entry = tk.Entry(root)

    # Create the submit button
    submit_button = tk.Button(root, text="Submit", command=submit)

    # Place the form fields on the screen
    name_label.grid(row=0, column=0)
    name_entry.grid(row=0, column=1)

    email_label.grid(row=1, column=0)
    email_entry.grid(row=1, column=1)

    password_label.grid(row=2, column=0)
    password_entry.grid(row=2, column=1)

    phone_number_label.grid(row=3, column=0)
    phone_number_entry.grid(row=3, column=1)
    submit_button.grid(row=4, column=1)


# Initialize the python classes to start the game
display = Display(0, 0)
paddle_a = SPaddle(-350, 0,selected_color)
paddle_b = SPaddle(350, 0,selected_color)
ball = Ball(0, 0)
score = Score(0, 250)
winner = Winner(0, 229)

if  __name__ == "__main__":
    # choose_clr()
    #calls the welocome windows for register or login
    create_welcome_window()


