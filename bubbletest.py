'''
    CS5001
    Spring 2019
    Test Suite for HW7
'''
from bubblefunctions import *
import unittest
import time
import os
import contextlib


class PlayerTest(unittest.TestCase):
    def test_init(self):
        testplayer = Player()
        self.assertFalse(testplayer.bullets_fired)
        self.assertFalse(testplayer.bullet_cooldown)
        self.assertFalse(testplayer.game_start)

    def test_begin(self):
        testplayer = Player()
        testplayer.begin()
        self.assertTrue(testplayer.game_start)

    def test_fire(self):
        testplayer = Player()
        testplayer.fire_bullet()
        self.assertTrue(testplayer.bullet_cooldown)
        self.assertNotEqual(testplayer.bullets_fired, [])

    def test_reload(self):
        testplayer = Player()
        testplayer.bullet_cooldown = True
        testplayer.reload()        
        self.assertFalse(testplayer.bullet_cooldown)

class Entity_SpawnTest(unittest.TestCase):
    def test_init(self):
        testentityspawn = Entity_Spawn()
        self.assertFalse(testentityspawn.corpses)
        self.assertFalse(testentityspawn.player_hit)
        self.assertEqual(testentityspawn.enemy_num, 10)
        self.assertFalse(testentityspawn.bullets)
        self.assertEqual(testentityspawn.targets_hit, 0)

    def test_populate(self):
        testentityspawn = Entity_Spawn()
        testentityspawn.populate(0)
        self.assertEqual(len(testentityspawn.enemies), 10)
        
        testentityspawn.populate(6)
        self.assertEqual(len(testentityspawn.enemies), 68)

    def test_move_enemies(self):
        testentityspawn = Entity_Spawn()
        testenemy = Enemy(0)
        testenemy.speed = 10
        testenemy.location = [0, 0]
        testentityspawn.enemies.append(testenemy)
        testentityspawn.move_enemies([100, 100])    #testing movement of onscreen enemies
        self.assertAlmostEqual(testentityspawn.enemies[0].location[0], ((.02 * 10) + (.1 * 1)))
        self.assertEqual(testentityspawn.enemies[0].location[1], 0)

        testenemy.location = [300, 0]   #testing movement of offscreen enemies
        testentityspawn.move_enemies([100, 100])
        self.assertEqual(testentityspawn.enemies[0].location[0], -255)
        self.assertEqual(testentityspawn.enemies[0].location[1], -50)           
        testenemy.location = [0, -300]
        testentityspawn.move_enemies([100, 100])
        self.assertEqual(testentityspawn.enemies[0].location[0], -600)

        testenemy.location = [100, 100]   #testing collision event
        testentityspawn.move_enemies([100, 100])
        self.assertTrue(testentityspawn.player_hit)

        testentityspawn.corpses.append([(0, 0), 1])    #testing enemy post-death event
        testentityspawn.corpses.append([(0, 5), 5])
        testentityspawn.move_enemies([100, 100])
        self.assertEqual(testentityspawn.corpses[0][1], 0)

    def test_move_bullets(self):
        testentityspawn = Entity_Spawn()
        test_bullet_list = [0, 1, 2]
        testentityspawn.move_bullets(test_bullet_list)
        self.assertEqual(len(testentityspawn.bullets), 3)
        self.assertEqual(testentityspawn.bullets[0].location[0], -2)
        self.assertEqual(testentityspawn.bullets[0].location[1], -198)

        testentityspawn.bullets[0].location[1] = 250    #testing offscreen bullets
        testentityspawn.move_bullets([])
        self.assertEqual(testentityspawn.bullets[0].location[0], -600)

        testenemy = Enemy(0)    #testing enemy collision event
        testentityspawn.enemies.append(testenemy)
        testenemy.location = [0, 0]
        testentityspawn.bullets[2].location[1] = 0
        testentityspawn.move_bullets([])
        self.assertEqual(testentityspawn.bullets[0].location[0], -600)
        self.assertEqual(testentityspawn.enemies[0].location[0], -600)

    def test_clean_up(self):
        testentityspawn = Entity_Spawn()
        testenemy = Enemy(0)
        testentityspawn.enemies.append(testenemy)
        testenemy.location = [-600, 0]
        test_bullet_list = [0]
        testentityspawn.move_bullets(test_bullet_list)
        testentityspawn.bullets[0].location[0] = -600
        testentityspawn.clean_up()

        self.assertEqual(testentityspawn.targets_hit, 1)
        self.assertFalse(testentityspawn.bullets)
        self.assertFalse(testentityspawn.enemies)
        
class Enemy_Test(unittest.TestCase):
    def test_init(self):
        testenemy = Enemy(1)
        self.assertNotEqual(testenemy.speed, 0)
        self.assertNotEqual(testenemy.speed, 30)
        self.assertNotEqual(testenemy.location[0], -2000)
        self.assertNotEqual(testenemy.location[0], 250)
        self.assertNotEqual(testenemy.location[1], 0)
        self.assertNotEqual(testenemy.location[1], 300)

class Bullet_Test(unittest.TestCase):
    def test_init(self):
        testbullet = Bullet(100)
        self.assertEqual(testbullet.location[0], 98)
        self.assertEqual(testbullet.location[1], -200)


class soundghost_test(unittest.TestCase):
    def test_init(self):
        testghost = Soundghost()
        self.assertFalse(testghost.sound_on)
        self.assertFalse(testghost.player_hit_file)
        self.assertFalse(testghost.start_sound_file)
        self.assertFalse(testghost.bgm1)
        self.assertFalse(testghost.bgm2)

    def asset_check_test(self):
        #test with no input
        testghost.asset_check() 
        self.assertFalse(testghost.sound_on)
        self.assertFalse(testghost.player_hit_file)
        self.assertFalse(testghost.start_sound_file)
        self.assertFalse(testghost.bgm1)
        self.assertFalse(testghost.bgm2)

        #test with positive input
        testghost.player_hit_file = 'player_hit.wav'
        testghost.start_sound_file = 'start.wav'
        testghost.bgm1 = 'mild.wav'
        testghost.bgm2 = 'spicy.wav'
        testghost.asset_check()
        self.assertEqual(testghost.player_hit_file, 'player_hit.wav')
        self.assertEqual(testghost.start_sound_file, 'start.wav')
        self.assertEqual(testghost.bgm1, 'mild.wav')
        self.assertEqual(testghost.bgm2, 'spicy.wav')

        #test with negative input
        testghost.player_hit_file = 'player_hitch.wav'
        testghost.start_sound_file = 'stars.wav'
        testghost.bgm1 = 'milk.wav'
        testghost.bgm2 = 'spices.wav'
        testghost.asset_check()
        self.assertFalse(testghost.player_hit_file)
        self.assertFalse(testghost.start_sound_file)
        self.assertFalse(testghost.bgm1)
        self.assertFalse(testghost.bgm2)

class miscfunction_test(unittest.TestCase):
    def test_collision_detection(self):
        self.assertFalse(collision_detected([100, 100],[250, 250]))
        self.assertTrue(collision_detected([95, 32],[100, 40]))

    def test_read_hi_score(self):
        with contextlib.suppress(FileNotFoundError):
            os.remove('hi_score_read_test.txt')
        testfile = open('hi_score_read_test.txt', 'w')
        testfile.write('1234 - TACOBEL')
        testfile.close()
        self.assertEqual(read_hi_score('hi_score_read_test.txt'), '1234 - TACOBEL')
        

    def test_write_hi_score(self):
        with contextlib.suppress(FileNotFoundError):
            os.remove('hi_score_write_test.txt')
        self.assertTrue(write_hi_score('hi_score_write_test.txt', 7188, 'turkey'))
        testfile = open('hi_score_write_test.txt', 'r')
        testfile_string = testfile.read()
        testfile.close()
        self.assertEqual(testfile_string, '7188 - TURKEY')
        
def sound_test():
    testghost = Soundghost()
    testghost.sound_on = True
    testghost.player_hit_file = 'player_hit.wav'
    testghost.start_sound_file = 'start.wav'
    testghost.bgm1 = 'mild.wav'
    testghost.bgm2 = 'spicy.wav'
    testghost.asset_check()
    if testghost.sound_on == True:
        try:
            testghost.start_sound()
            testghost.player_hit_sound()
            testghost.background_music()
            time.sleep(6)
            testghost.silence_bgm()
            testghost.alternate_bgm()
            testghost.background_music()
            time.sleep(6)
            testghost.silence_bgm()
        except RuntimeError:
            #PROBLEM PLAYING SOUNDS
            print('error playing sounds')
    else:
        print('sound off')

def screen_test():
    screen = turtle.Screen()
    screen.bgcolor('black')
    testnarrator = Narrator()
    testnarrator.voice.clear()
    testnarrator.start_screen()
    time.sleep(1)
    testnarrator.voice.clear()
    testnarrator.wave_complete()
    time.sleep(1)
    testnarrator.voice.clear()
    testnarrator.time_out()
    time.sleep(1)
    testnarrator.voice.clear()
    testnarrator.name_entry()
    time.sleep(1)
    testnarrator.voice.clear()
    testnarrator.game_over()
    time.sleep(1)
    testnarrator.voice.clear()

def scoreboard_test():
    screen = turtle.Screen()
    screen.bgcolor('white')
    testboard = Scoreboard()
    testboard.draw_hi_score(9999)
    testboard.draw_time(999)
    testboard.draw_score(999)
    testboard.draw_lvl(999)
    time.sleep(2)
    screen.clear()    


def main():
     
    unittest.main()

    ###comment out the unit test and uncomment below for the sound and screen tests
    #print('now commencing screen test')
    #screen_test()   
    #scoreboard_test()

    #print('now commencing sound test')
    #sound_test()

    #print('all tests complete')
    
main()
