import turtle
import random
import time
from bubblefunctions import *


###HI SCORE FILE###
HI_SCORE_FILE = 'hi_score.txt'

###IMAGES###
PLAYER_IMAGE = 'mug.gif'
ENEMY_IMAGE = 'bubble.gif'
BULLET_IMAGE = 'nail.gif'
HIT_IMAGE = 'pop.gif'

###SOUND###
SOUND = True
PLAYER_HIT_SOUND = 'player_hit.wav'
TARGET_HIT_SOUND = 'bubble_pop.wav'
START_SOUND = 'start.wav'
BGM1 = 'mild.wav'
BGM2 = 'spicy.wav'

##GAME CONSTANTS FOR TIME##
LVL_LENGTH = 66
GAME_SPEED = 250


def main():
    ###SETUP###
    screen = turtle.Screen()    # assembling Screen, preparing images
    screen.setup(500,500)      
    screen.tracer(0)            
    screen.bgcolor('black')
    screen.register_shape(PLAYER_IMAGE)
    screen.register_shape(ENEMY_IMAGE)
    screen.register_shape(HIT_IMAGE)
    screen.register_shape(BULLET_IMAGE)
    
    sounds = Soundghost()   # getting sounds ready
    sounds.player_hit_file = PLAYER_HIT_SOUND
    sounds.start_sound_file = START_SOUND
    sounds.bgm1 = BGM1
    sounds.bgm2 = BGM2
    sounds.asset_check()
    sounds.sound_on = SOUND

    narrator = Narrator()   # initializing the scoreboard and screen info
    scoreboard = Scoreboard()

    p1 = Player()   # initializing the turtles responsible for player and enemies
    p1.player.shape(PLAYER_IMAGE)
    swarm = Entity_Spawn()
    swarm.enemy_spawn.shape(ENEMY_IMAGE)
    swarm.enemy_hit_spawn.shape(HIT_IMAGE)
    swarm.bullet_spawn.shape(BULLET_IMAGE)

    hi_score = read_hi_score(HI_SCORE_FILE).split()    # grabbing hi score, setting start values
    game_time =  LVL_LENGTH
    round_counter = GAME_SPEED
    lvl = 1
    score = 0
    score_bonus = 0

    scoreboard.draw_hi_score(" ".join(hi_score))    # drawing scoreboard
    scoreboard.draw_time(game_time)
    scoreboard.draw_score(score)
    scoreboard.draw_lvl(lvl)

    screen.listen() # readying turtle for player input

    ###START SCREEN###
    while p1.game_start == False:       # hold here until player presses 'b' to start or 'q' to quit
        narrator.start_screen()
        screen.onkey(p1.begin, "b")
        screen.onkey(p1.begin, "B")
        screen.onkey(sounds.alternate_bgm, "S")
        screen.onkey(quit, "q")
        screen.onkey(quit, "Q")

    ###GAME START###
    screen.onkey(None, "b")    # removing unnecessary keybinding, starting controls
    screen.onkey(None, "B")
    screen.onkey(p1.move_left, "Left")
    screen.onkey(p1.move_right, "Right")
    screen.onkey(p1.fire_bullet, "space")

    narrator.voice.clear()  # clearing screen, starting music, adding enemies
    sounds.start_sound()
    time.sleep(1)
    sounds.background_music()
    swarm.populate(0)

    while p1.game_start == True:
        score = swarm.targets_hit * 10 + score_bonus    # tracking score
        if round_counter == 0:    # tracking game clock
            game_time -= 1
            scoreboard.draw_time(game_time)
            round_counter = GAME_SPEED
        
        if len(swarm.enemies) == 0:    # checking for completed wave
            narrator.wave_complete()
            screen.ontimer(narrator.voice.clear, t=2500)
            swarm.populate(lvl)
            lvl += 1
            scoreboard.draw_lvl(lvl)
            score_bonus += int((game_time * (1 + (lvl * 0.1))))   # reward player with bonus points and time
            game_time = game_time + 10
        if game_time == 0:    # checking for timeout
            narrator.time_out()
            screen.ontimer(narrator.voice.clear, t=2500)
            swarm.populate(lvl)
            lvl += 1
            scoreboard.draw_lvl(lvl)
            game_time = LVL_LENGTH 
            
        if swarm.player_hit == True:    # checking for player hit
            break

        swarm.enemy_spawn.clear()    # clearing frame
        swarm.enemy_hit_spawn.clear()
        swarm.bullet_spawn.clear()
        
        swarm.move_enemies(p1.player.pos())   # moving frame
        swarm.move_bullets(p1.bullets_fired)
        
        swarm.clean_up()    # clearing dead enemies/spent bullets

        scoreboard.draw_score(score)    # updating score
        
        screen.update()    # updating screen and internal gametime
        round_counter -= 1


    ##GAME OVER###
    sounds.silence_bgm() # stopping music, playing player hit noise
    sounds.player_hit_sound()
    time.sleep(0.5)
            
    if score > int(hi_score[0]):    #checking for hi score, taking player's name and writing to hi_score file
        narrator.name_entry()    
        player_name = ((screen.textinput('x _ x', 'add ur name to the hall of fame'))[:5])
        write_hi_score(HI_SCORE_FILE, score, player_name)
        hi_score = read_hi_score(HI_SCORE_FILE).split()
        scoreboard.draw_hi_score(" ".join(hi_score))

    narrator.voice.clear()  # clearing screen of announcements
    narrator.game_over()    # announcing game end, auto close after 8 seconds
    screen.ontimer(screen.bye, 8000)

main()



