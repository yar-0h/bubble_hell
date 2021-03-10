import turtle
import random
import winsound
import sys
import os.path
from os import path

ENEMY_MOD = 1
ENEMY_SPEED_MOD = 1

###CLASSES###
#player class
class Player:
    def __init__(self):
        self.player = turtle.Turtle()
        self.screen = turtle.Screen()
        self.player.penup()
        self.player.color('white')
        self.player.shape('square')
        self.player.hideturtle()
        self.player.sety(-200)
        self.player.showturtle()      

        self.bullets_fired = []
        self.bullet_cooldown = False

        self.game_start = False

    def begin(self):
        '''
        name: begin
        description: switches the class' game_start attribute to 'True', starting the game
        input: None
        output: None
        '''
        self.game_start = True

    def move_left(self):
        '''
        name: move_left
        description: moves player icon to the left, stopping at the leftmost edge of the screen
        input: None
        output: None
        '''
        if self.player.xcor() > -250:
            self.player.setx(self.player.xcor()-8)

    def move_right(self):
        '''
        name: move_right
        description: moves player to the left, stopping at the rightmost edge of the screen
        input: None
        output:None
        '''
        if self.player.xcor() < 250:
            self.player.setx(self.player.xcor()+8)

    def fire_bullet(self):
        '''
        name: fire_bullet
        description: creates an instance of a Bullet Object, so long as inhibiting parameters allow
        input: None
        output: None
        '''
        if len(self.bullets_fired) < 1 and self.bullet_cooldown == False:
            self.bullets_fired.append(self.player.xcor())
            self.bullet_cooldown = True
            self.screen.ontimer(self.reload, 800)

    def reload(self):
        '''
        name: reload
        description: switches bullet_cooldown attribute to False, potentially preventing rapid fire
        input: None
        output: None
        '''
        self.bullet_cooldown = False
        

#entity spawn class  - draws frames containing enemies, bullets, and destroyed enemies      
class Entity_Spawn:
    def __init__(self):
        self.enemy_spawn = turtle.Turtle()
        self.enemy_spawn.penup()
        self.enemy_spawn.color('white')
        self.enemy_spawn.shape('circle')
        self.enemy_spawn.hideturtle()
        self.enemy_spawn.speed(0)

        self.enemy_hit_spawn = turtle.Turtle()
        self.enemy_hit_spawn.penup()
        self.enemy_hit_spawn.color('black')
        self.enemy_hit_spawn.shape('circle')
        self.enemy_hit_spawn.hideturtle()
        self.enemy_hit_spawn.speed(0)
        self.hit_layer = turtle.Screen()
        self.corpses = []

        self.bullet_spawn = turtle.Turtle()
        self.bullet_spawn.penup()
        self.bullet_spawn.color('white')
        self.bullet_spawn.shape('arrow')
        self.bullet_spawn.hideturtle()
        self.bullet_spawn.speed(0)

        self.player_hit = False
        self.enemies = []
        self.enemy_num = 10 * ENEMY_MOD
        self.bullets = []
        self.targets_hit = 0

    def populate(self, lvl):
        '''
        name: populate
        description: creates and draws a number of enemy objects onto the screen
        input: integer, representing the game levl
        output: none
        '''
        if lvl == 0:
            self.enemies = [ Enemy(lvl) for i in range(self.enemy_num)]
        else:
            for i in range(self.enemy_num + 8 * lvl):
                self.enemies.append(Enemy(lvl))
        for i in range(len(self.enemies)):
            self.enemy_spawn.goto(self.enemies[i].location)
            self.enemy_spawn.stamp()
        
    def move_enemies(self, player_pos):
        '''
        name: move enemies
        description: updates positions of onscreen enemies and redraws them
                     checks for collisions between enemies and player
        input: cartesian coordinates indicating the player's position.
        output: None
        '''
        for i in range(len(self.enemies)):
            self.enemies[i].location[0] += (0.02 * self.enemies[i].speed) + (0.1 * ENEMY_SPEED_MOD)
            if self.enemies[i].location[0] > 255:
                self.enemies[i].location[0] = -255
                self.enemies[i].location[1] -= 50
            if self.enemies[i].location[1] < -255:
                self.enemies[i].location[0] = -600
            if collision_detected((self.enemies[i].location[0], self.enemies[i].location[1]), (player_pos)):
                self.player_hit = True
        for i in range(len(self.enemies)):
            self.enemy_spawn.goto(self.enemies[i].location)
            self.enemy_spawn.stamp()
        for i in range(len(self.corpses)):
            self.enemy_hit_spawn.goto(self.corpses[i][0])
            self.enemy_hit_spawn.stamp()
            self.corpses[i][1] -= 1            

    def move_bullets(self, bullet_list):
        '''
        name: move bullets
        description: updates position of onscreen bullets and redraws them
                     checks for collisions between bullets and enemies,
                     changing both's position to 'graveyard' if applicable
        input: a list of created bullet entities
        output: None
        '''
        if len(bullet_list) > 0:
            self.bullets = [ Bullet(bullet_list[i]) for i in range(len(bullet_list))]
            bullet_list.pop()
        if len(self.bullets) > 0:
            for i in range(len(self.bullets)):
                self.bullets[i].location[1] += 2
                if self.bullets[i].location[1] > 230:
                    self.bullets[i].location[0] = -600
                for j in range(len(self.enemies)):
                    if collision_detected((self.enemies[j].location[0], self.enemies[j].location[1]), (self.bullets[i].location[0], self.bullets[i].location[1])):
                        self.corpses.append([(self.enemies[j].location[0], self.enemies[j].location[1]), 50])
                        self.enemies[j].location[0] = -600
                        self.bullets[i].location[0] = -600
            for i in range(len(self.bullets)):
                self.bullet_spawn.goto(self.bullets[i].location)
                self.bullet_spawn.stamp()
                                               
    def clean_up(self):
        '''
        name: clean_up
        description: checks for entities in the 'grave' location, removes them 
        input: None
        output: None
        '''
        enemy_grave = []
        bullet_grave = []
        for i in range(len(self.enemies)):
            if self.enemies[i].location[0] == -600:
                enemy_grave.append(i)
                self.targets_hit += 1
        for i in range(len(self.bullets)):
            if self.bullets[i].location[0] == -600:
                bullet_grave.append(i)
        try:
            for i in range(len(enemy_grave)):
                self.enemies.pop(enemy_grave[i])
            for i in range(len(bullet_grave)):
                self.bullets.pop(bullet_grave[i])
            for i in range(len(self.corpses)):
                if self.corpses[i][1] - 10 <= 0:
                    self.corpses.pop(i)
        except IndexError:      
                pass
                #sometimes this brings up an index error, i believe it's due to the sketchy timing of things


#enemy class  -  tracks speed and location of individual enemies, takes an integer representing the game's current 'level'
class Enemy:
    def __init__(self, lvl):
        self.speed = random.randrange(5, (15 + 5 * lvl))
        self.location = [random.randrange(-250, 250) - 800, random.randrange(80, 200)]
        if 0 < lvl < 20:
            self.location[1] -= random.randrange(0, (10 * lvl))


#bullet class  -  created at the position of the player        
class Bullet:
    def __init__(self, player_xcor):
        self.location = [(player_xcor - 2), -200]


#narrator class  -  draws informative strings on the screen
class Narrator:
    def __init__(self):
        self.voice = turtle.Turtle()
        self.voice.penup()
        self.voice.hideturtle()
        self.voice.color('white')

    def start_screen(self):
        '''
        name: start_screen
        description: tells the narrator to draw the title screen
        input: None
        output: None
        '''
        self.voice.goto(-230, -230)
        self.voice.color('red')
        self.voice.write("OR  ", True, align = "left", font = ('fixedsys', 12, 'normal'))
        self.voice.color('white')
        self.voice.write("press 'Q' at any time to quit", align = "left", font = ('fixedsys', 10, 'normal'))
        self.voice.goto(-210, 140)
        self.voice.write("Welcome to", align = "left", font = ('fixedsys', 15, 'bold'))
        self.voice.goto(-110, 75)
        self.voice.write("B U B B L E", align = "center", font = ('fixedsys', 32, 'bold'))
        self.voice.goto(150, 75)
        self.voice.color('red')
        self.voice.write("H E L L", align = "center", font = ('fixedsys', 32, 'bold'))
        self.voice.goto(0, -50)
        self.voice.color('white')
        self.voice.write("Press 'B' to Begin", align = "center", font = ('fixedsys', 20, 'bold'))

    def wave_complete(self):
        '''
        name: wave_complete
        description: instructs the narrator to draw text, informing player of completed wave
        input: None
        output: None
        '''
        self.voice.goto(-110, 75)
        self.voice.write("W A V E", align = "center", font = ('fixedsys', 32, 'bold'))
        self.voice.goto(0, -20)
        self.voice.color('red')
        self.voice.write("C O M P L E T E", align = "center", font = ('fixedsys', 32, 'bold'))
        self.voice.goto(-60, -90)
        self.voice.color('white')
        self.voice.write(";)", align = "center", font = ('fixedsys', 32, 'bold'))

    def time_out(self):
        '''
        name: time_out
        description: tells the narrator to draw text in the event of time running out
        input: None
        output: None
        '''
        self.voice.goto(-210, 140)
        self.voice.color('red')
        self.voice.write("M  O  R  E", align = "left", font = ('fixedsys', 15, 'bold'))

    def name_entry(self):
        '''
        name: name_entry
        description: informs the player that they got the high score
        input: none
        output: none
        '''
        self.voice.goto(0, 75)
        self.voice.write("YOU GOT \nTHE HIGH SCORE", align = "center", font = ('fixedsys', 26, 'bold'))
        self.voice.goto(75, -80)
        self.voice.color('red')
        self.voice.write("GOOD JOB ;D", align = "center", font = ('fixedsys', 26, 'bold'))
        

    def game_over(self):
        '''
        name: game_over
        description: draws the 'game_over' screen
        input: none
        output: none
        '''
        self.voice.goto(-80, 75)
        self.voice.write("G A M E", align = "center", font = ('fixedsys', 32, 'bold'))
        self.voice.goto(0, -20)
        self.voice.color('red')
        self.voice.write("O V E R ; - ;", align = "center", font = ('fixedsys', 32, 'bold'))

#scoreboard class  -  manages the top portion of the screen and relevent numbers
class Scoreboard:
    def __init__(self):
        self.back = turtle.Turtle()
        self.back.hideturtle()
        self.back.shape('square')
        self.back.fillcolor('white')
        self.back.shapesize(1.75, 26)
        self.back.goto(-5, 235)
        self.back.stamp()

        self.heading = Scorepost()
        self.heading.pen.goto(-240, 233)
        self.heading.pen.color('red')
        self.heading.pen.write(('H I - S C O R E      T I M E     S C O R E     L V L'), font = ('fixedsys', 14, 'bold'))

        self.high_score = Scorepost()
        self.score = Scorepost()
        self.time = Scorepost()
        self.lvl = Scorepost()
    
    def draw_hi_score(self, hi_score):
        '''
        name: draw_hi_score
        description: writes the current high score to the scoreboard
        input: an integer, the current high score
        output: None
        '''
        self.high_score.pen.clear()
        self.high_score.pen.goto(-241, 218)
        self.high_score.pen.write(hi_score, font = ('fixedsys', 14, 'bold'))

    def draw_time(self, time):
        '''
        name: draw_time
        description: writes the round's remaining time to the scoreboard
        input: an integer, the round's remaining time
        output: None
        '''
        self.time.pen.clear()
        self.time.pen.goto(-51, 218)
        self.time.pen.write(time, font = ('fixedsys', 14, 'bold'))

    def draw_score(self, score):
        '''
        name: draw_score
        description: writes the current score to the scoreboard
        input: an integer, the current score
        output: None
        '''
        self.score.pen.clear()
        self.score.pen.goto(56, 218)
        self.score.pen.write(score, font = ('fixedsys', 14, 'bold'))

    def draw_lvl(self, lvl):
        '''
        name: draw_lvl
        description: writes the current level to the scoreboard
        input: an integer, the game's current level
        output: None
        '''
        self.lvl.pen.clear()
        self.lvl.pen.goto(182, 218)
        self.lvl.pen.write(lvl, font = ('fixedsys', 14, 'bold'))


#scorepost class  -  individual entries upon the scoreboard
class Scorepost:
    def __init__(self):
        self.pen = turtle.Turtle()
        self.pen.penup()
        self.pen.hideturtle()
        self.pen.color('black')


#soundghost class  -  manages the sounds heard in the game
    #uses the winsound module, which enables simple sounds without a third party module
    #unfortunately, doesn't work on anything other than windows
    #in which case, runtimeerrors will be raised, which should be caught
    #winsound flags SND_ASYNC and SND_NOSTOP allow the sound to be played without stalling the program or interrupting any other noises, respectively
class Soundghost:
    def __init__(self):
        self.sound_on = False
        self.player_hit_file = False
        self.start_sound_file = False
        self.bgm1 = False
        self.bgm2 = False

    def asset_check(self):
        '''
        name: asset_check
        description: checks to see if appropriate sounds exist, uses them if so
        input: None
        output: None
        '''
        if path.exists(self.player_hit_file) == False:
            self.player_hit_file = None
        if path.exists(self.start_sound_file) == False:
            self.start_sound_file = None
        if path.exists(self.bgm1) == False:
            self.bgm1 = None
        if path.exists(self.bgm2) == False:
            self.bgm2 = None

    def player_hit_sound(self):
        '''
        name: player_hit_sound
        description: plays the player_hit sound
        input: None
        output: None
        '''
        if self.sound_on == True:
            try:
                winsound.PlaySound(self.player_hit_file, winsound.SND_NOSTOP | winsound.SND_ASYNC)
            except RuntimeError:
                #PROBLEM PLAYING SOUNDS
                pass                
                                     
    def start_sound(self):
        '''
        name: start_sound
        description: plays the start sound
        input: None
        output: None
        '''
        if self.sound_on == True:
            try:
                winsound.PlaySound(self.start_sound_file, winsound.SND_NOSTOP | winsound.SND_ASYNC)
            except RuntimeError:
                #PROBLEM PLAYING SOUNDS
                pass
                
    def background_music(self):
        '''
        name: background_music
        description: starts playing the game's background music on a loop.
        input: None
        output: None
        '''
        if self.sound_on == True:
            try:
                pass
                winsound.PlaySound(self.bgm1, winsound.SND_ASYNC | winsound.SND_LOOP)
            except RuntimeError:
                #PROBLEM PLAYING SOUNDS
                pass
                
                            
    def silence_bgm(self):
        '''
        name: silence_bgm
        description: stops any background music that might be playing (any other sounds too, but that should be less noticeable as they arent on a loop)
        input: None
        output: None
        '''
        if self.sound_on == True:
            try:
                winsound.PlaySound(None, winsound.SND_FILENAME)
            except RuntimeError:
                #PROBLEM PLAYING SOUNDS
                pass

    def alternate_bgm(self):
        '''
        name: alternate_bgm
        description: swaps the regular bgm with an alternate, potentially secret bgm
        input: None
        output: None
        '''
        if self.bgm2 != False:
            self.bgm1 = self.bgm2        



###FUNCTIONS###
def collision_detected(object1_coordinates, object2_coordinates):
    '''
    name: collision_detected
    description: checks to see if two pairs of coordinates are within a particular distance of eachother
    input: two sets of cartesian coordinates
    output: a boolean, indicating whether the objects are close or not
    notes: the values concerning the hit detection are the result of guessing and checking.
           It's pretty close and definitely sufficient for these purposes but its not flawless, mostly due to variations in image shape/size
    '''
    if (abs(object1_coordinates[0] - object2_coordinates[0]) < 27) and (abs(object1_coordinates[1] - object2_coordinates[1]) < 30):
        return True
    else:
        return False

def read_hi_score(filename):
    '''
    name: read_hi_score
    description: attempts to open up a file containing the game's current high score and scoreholder
    input: the name of a .txt file containing the formatted high score data to be read
    output: returns the contents of the high score file,
            returns an ERROR string if errors are encountered
    '''
    try:
        hi_score_infile = open(filename, 'r')
        hi_score = hi_score_infile.read()
        hi_score_infile.close()
        if hi_score == '':
            return '000 - UwU'
        return hi_score
    except OSError:
        return ('000 - ERROR')       

def write_hi_score(filename, score, scoreholder_name):
    '''
    name: write_hi_score
    description: attempts to write a new high score entry over the current high_score file, prints ERROR to console if error is encountered
    input: a filename representing the relevant high score .txt file, an integer representing the player's score and a string representing the scoreholder's identity
    output: None
    '''
    try:
        hi_score_outfile = open(filename, 'w')
        hi_score =(str(score) + ' - ' + scoreholder_name.upper())
        hi_score_outfile.write(hi_score)
        hi_score_outfile.close()
        return True
    except OSError:
        print("ERROR WRITING FILE")
        return

