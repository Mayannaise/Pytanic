# Written by: Owen Jeffreys
# Date modified: 26-May-2018
# Copyright 2018 all rights reserved


import random, os.path, sys
import pygame
import math
import operator
from pygame.locals import *
import Tkinter
root = Tkinter.Tk()

TITLE = "Pytanic Educational"

SCREEN_HEIGHT = 480    #laptop
SCREEN_WIDTH = 740     #laptop
#SCREEN_HEIGHT = 480    #pi ??
#SCREEN_WIDTH = 400     #pi ??
#SCREEN_HEIGHT = 960     #hdtv
#SCREEN_WIDTH = 1480     #hdtv



if root.winfo_screenheight() < SCREEN_HEIGHT or root.winfo_screenwidth() < SCREEN_WIDTH:
    SCREEN_HEIGHT = int(root.winfo_screenheight()*0.8)  #auto
    SCREEN_WIDTH = int(root.winfo_screenwidth()*0.8)    #auto

SCREEN_BORDER = 20
SCREENRECT = Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)   #game & console size
CONSOLE_WIDTH = 180

FRAMES_PER_SEC = 20     #cap fps to save mem
SPLASH_DISPLAY = 5000   #length to display spash screens for
REVIEW_TIME = 300       #length to display mistake, before showing fail screen
SHIP_SPEED = 4          #n pixels ship moves per frame

MAX_ICEBERGS = 5    #number of Icebergs in water
MAX_ISLANDS = 2     #number of Islands in water
MAX_SHARKS = 3      #number of sharks in water

#PROG_DIR = os.path.split(os.path.abspath(__file__))[0]     #program's directory
PROG_DIR = "."                                              #program's directory

RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,100,255)


class Res: pass     #container for images
dirtyRects = []     #list of update_rects
shipCmds = ["start", "move", "turn", "sos"]       #list of user inputted commands
userCmds = []       #list of user inputted commands
myScore = 0         #score for this session
topScores = []      #as read in from score file
scoreFile = "scores.txt"    #top scores stored for all sessions
name = "Me"
ship = None
compass = None
obstacles = None
ammo = None
cmdWin = None
port = None
mapScale = None





class Actor:
    def __init__(self, image):
        self.isIceberg = 0
        self.isShip = 0
        self.isShark = 0
        self.image = image
        self.rect = image.get_rect()
        
    def update(self):
        pass
    
    def draw(self, screen):
        r = screen.blit(self.image, self.rect)
        dirtyRects.append(r)
        
    def erase(self, screen, background):
        r = screen.blit(background, self.rect, self.rect)
        dirtyRects.append(r)



#the actual programmable ship
class Ship(Actor):
    def __init__(self):
        Actor.__init__(self, Res.ship)
        self.isShip = 1
        self.alive = 1
        self.angle = 0
        self.rect.centerx = SCREENRECT.centerx
        self.rect.bottom = SCREENRECT.bottom

    def move(self, dist):
##        if self.angle % 360 == 0 or self.angle == 0:   #forward
##            self.rect.centery = self.rect.centery - dist
##        elif self.angle % 270 == 0:    #left
##            self.rect.centerx = self.rect.centerx - dist
##        elif self.angle % 180 == 0:    #backward
##            self.rect.centery = self.rect.centery + dist
##        elif self.angle % 90 == 0:      #right
##            self.rect.centerx = self.rect.centerx + dist
    
        self.rect.centerx = self.rect.centerx + (dist * math.sin(math.radians(self.angle)))
        self.rect.centery = self.rect.centery - (dist * math.cos(math.radians(self.angle)))

    def turn(self, degrees):
        self.angle = self.angle + degrees
        self.image = pygame.transform.rotate(self.image, -degrees)
        r = self.rect
        self.rect = self.image.get_rect()
        self.rect.centerx = r.centerx
        self.rect.centery = r.centery




#slowly drifting icebergs
class Iceberg(Actor):
    def __init__(self):
        Actor.__init__(self, Res.iceberg)
        self.isIceberg = 1
        self.maxDist = random.randrange(2, 6)   #how far it is allowed to move
        self.travel = 0     #how far has it gone
        self.direction = 1 #speed
        self.axis = random.randrange(0, 2)  #start diretion
        self.rect.left = random.randrange(0, SCREENRECT.right-self.rect.width)
        self.rect.top = random.randrange(0, SCREENRECT.bottom-self.rect.height-Res.ship.get_height())
            
    def update(self):
        self.rect[self.axis] = self.rect[self.axis] + self.direction
        self.travel = self.travel + self.direction
        if self.travel == self.maxDist:
            self.axis = not self.axis
            self.travel = 0
            if not self.axis:    #if vertical axis, do not change direction
                self.direction = -self.direction
                self.maxDist = -self.maxDist



#back and forth sharks
class Shark(Actor):
    def __init__(self):
        Actor.__init__(self, Res.shark)
        self.isShark = 1
        self.speed = random.randrange(1, 3)
        self.dir = self.rect.height
        self.rect.left = random.randrange(0, SCREENRECT.right-SCREEN_BORDER-self.rect.width)
        self.rect.top = random.randrange(SCREEN_BORDER, SCREENRECT.bottom-SCREEN_BORDER-self.rect.height)  #y-axis level
            
    def update(self):
        self.rect.left = self.rect.left + self.speed

        if (self.rect.right > SCREENRECT.right-self.speed or self.rect.left < 0): #if off sides of screen, turn around
            self.speed = -self.speed
            self.image = pygame.transform.flip(self.image, 1, 0)
            self.rect.top = self.rect.top + self.dir

        #if (self.rect.bottom > SCREENRECT.bottom-Res.ship.get_height()): #if off bottom of screen, turn around
        if (self.rect.bottom > SCREENRECT.bottom): #if off bottom of screen, turn around
            self.dir = -self.dir
            #self.rect.bottom  = SCREENRECT.bottom-Res.ship.get_height()
            self.rect.bottom  = SCREENRECT.bottom
        elif (self.rect.top < 0):    #if off top of screen, turn around
            self.dir = -self.dir
            self.rect.top  = SCREENRECT.top




#shark food (cheese)
class SharkFood(Actor):
    def __init__(self, x,y):
        Actor.__init__(self, Res.sharkfood)
        self.rect.centerx = x
        self.rect.centery = y

    def update(self):
        #self.rect.centery = self.rect.centery - 5
        pass


            

#stationary island
class Island(Actor):
    def __init__(self):
        Actor.__init__(self, Res.island)
        self.isIsland = 1
        self.rect.left = random.randrange(0, SCREENRECT.right-self.rect.width)
        self.rect.top = random.randrange(0, SCREENRECT.bottom-self.rect.height-Res.ship.get_height())




#stationary destination port
class Port(Actor):
    def __init__(self):
        Actor.__init__(self, Res.port)
        self.rect.left = 10
        self.rect.top = 10




#stationary map scale
class MapScale():
    def __init__(self):
        self.step = 40
        w = (self.step*5)
        h = 20
        self.rect = Rect(SCREEN_WIDTH-w-10, SCREEN_HEIGHT-h-10, w, h)
        self.surf = pygame.Surface(self.rect.size)
        self.font = pygame.font.SysFont("Courier", 12, 0)
        

    def draw(self, screen, background):
        r = self.surf.blit(background, self.rect, self.rect)
        
        c = 0
        for i in range(0, self.rect.width, self.step):
            pygame.draw.rect(self.surf, (c,c,c), (i,0,self.step+i,5), 0)
            text = self.font.render(str(i/SHIP_SPEED), 1, (255,0,0))
            self.surf.blit(text, (i, 7))
            if c==0: c=255
            else: c=0
        
        r = screen.blit(self.surf, self.rect)  #copy temp buffer to screen buffer
        dirtyRects.append(r)    #make note of rects to refresh later




#stationary navigational compass rose
class CompassRose(Actor):
    def __init__(self):
        Actor.__init__(self, Res.compassRose)
        self.rect.left = 10
        self.rect.bottom = SCREENRECT.bottom - 10
                



#command window
class CmdWin():
    def __init__(self, screen):
        self.CONSOLERECT = Rect(SCREENRECT.right, 0, CONSOLE_WIDTH, SCREENRECT.height)
        self.rect = self.CONSOLERECT
        self.setup()
        self.font = pygame.font.SysFont("Courier", 12, 1)
        self.welcome = "Welcome to Pytanic"
        pygame.draw.rect(screen, (0,0,0), self.CONSOLERECT, 0)
        #pygame.draw.rect(screen, (255,255,255), self.CONSOLERECT, 0)
        #pygame.draw.rect(screen, (0,0,0), self.CONSOLERECT, 3)
        self.write(screen, self.welcome, col=BLUE)
		
    def setup(self):
        self.line = self.CONSOLERECT.top
        self.margin = 6
        self.start = 0
        self.lineSpacing = 20
		
    def write(self, screen, text, newLine=1, col=(255,255,255)):
        #block = self.font.render(text, 1, (0,0,0))
        block = self.font.render(text, 1, col)
        l = self.rect.left+self.margin+self.start
        rect = block.get_rect(x=l, y=self.line+self.margin)
        blank = Rect(rect.x, rect.y, self.rect.width, rect.height)
        if self.start == 0: self.start = rect.width
        if newLine: #if on new line
            self.line += self.lineSpacing
            self.start = 0
        screen.fill((0,0,0), blank)   #paint over old text
        screen.blit(block, rect)        #put new text down
        pygame.display.update(blank)     #update this line

    def clear(self, screen):
        self.setup()
        pygame.draw.rect(screen, (0,0,0), self.CONSOLERECT, 0)
        self.write(screen, self.welcome, col=BLUE)
        pygame.display.update(self.CONSOLERECT)
        


#function to load img into resource container
def load_image(f, transparent):
    f = os.path.join(PROG_DIR, 'data', f)
    try:
        surface = pygame.image.load(f)
    except pygame.error:
        print pygame.get_error()
        exit()

    if transparent:
        corner = surface.get_at((0, 0)) #get transparent pixel
        surface.set_colorkey(corner, RLEACCEL)
    
    return surface.convert()





#return new dimensions to fit image in screen
def scale_img(img, incConsole = 1):
    if incConsole: w = (CONSOLE_WIDTH+SCREEN_WIDTH)
    else: w = SCREEN_WIDTH
    
    if img.get_width()/w > img.get_height()/SCREEN_HEIGHT:
        w = float(w)
        h = (w/img.get_width())*img.get_height()
    else:
        h = float(SCREEN_HEIGHT)
        w = (h/img.get_height())*img.get_width()
        
    return (int(w), int(h))




#paint text and image to screen
def load_screen(screen, subtitle, col, flip=1, width=0, footer=""):
    if width == 0: width = SCREEN_WIDTH
    else: width = screen.get_width()
    
    text = pygame.font.Font(None, 36).render(TITLE, 1, col)
    textpos = text.get_rect(y=10, centerx=width/2)
    screen.blit(text, textpos)
    
    text = pygame.font.Font(None, 24).render(subtitle, 1, col)
    textpos = text.get_rect(y=50, centerx=width/2)
    screen.blit(text, textpos)

    text = pygame.font.Font(None, 20).render(footer, 1, col)
    textpos = text.get_rect(y=SCREEN_HEIGHT-20, x=10)
    screen.blit(text, textpos)
    
    if flip: pygame.display.flip()


    

#obstacle collision routine
def collision(img, screen):
    pygame.time.wait(REVIEW_TIME)
    screen.fill((0,0,0))
    screen.blit(img, ((screen.get_width()/2)-(img.get_width()/2),0))  #load fail screen

    load_screen(screen, '( mission failed )', BLUE, 1, 1)



#mission failed routine
def mission_failed(screen):
    pygame.time.wait(REVIEW_TIME)
    pygame.draw.rect(screen, (0,0,0), (SCREENRECT), 0)
    screen.blit(Res.splash, ((SCREEN_WIDTH/2)-(Res.splash.get_width()/2),0))
    load_screen(screen, '( mission failed )', BLUE, 0)
    x = (SCREEN_WIDTH/2)-(Res.wrong.get_width()/2)
    y = (SCREEN_HEIGHT/2)-(Res.wrong.get_height()/2)
    screen.blit(Res.wrong, (x,y))
    pygame.display.flip()



#mission succeeded routine
def mission_completed(screen):
    pygame.time.wait(REVIEW_TIME)
    pygame.draw.rect(screen, (0,0,0), (SCREENRECT), 0)
    screen.blit(Res.splash, ((SCREEN_WIDTH/2)-(Res.splash.get_width()/2),0))
    load_screen(screen, '( mission complete )', BLUE, 0)
    x = (SCREEN_WIDTH/2)-(Res.correct.get_width()/2)
    y = (SCREEN_HEIGHT/2)-(Res.correct.get_height()/2)
    screen.blit(Res.correct, (x,y))
    pygame.display.flip()
    



#clear screen of actors
def clear_actors(screen, bgSurf):
    global obstacles, compass, ship, ammo, port
    for actor in obstacles + [compass] + [ship] + ammo + [port]:
        actor.erase(screen, bgSurf)



#update actors' positions etc, then display
def refresh_actors(screen, bgSurf):
    global dirtyRects, obstacles, compass, ship, ammo, port
    for actor in obstacles + [compass] + [ship] + ammo + [port]:
        actor.update()

    for actor in obstacles + [ship] + ammo + [compass] + [port]: #IN THIS ORDER ONLY
        actor.draw(screen)

    mapScale.draw(screen, bgSurf)
    
    pygame.display.update(dirtyRects)   #only update areas which need to be
    dirtyRects = []




###pixel check for collisions
##def check_collisions(ship, obstacles):
##    for x in range(0, ship.image.get_width()):
##        for y in range(0, ship.image.get_height()):
##            if ship.image.pixel(x, y) == not ship.image.pixel(0,0):
##                for actor in obstacles:
##                    for x2 in range(0, actor.image.get_width()):
##                        for y2 in range(0, actor.image.get_height()):
##                            pass
                        





#start up function
def main():
    global dirtyRects, obstacles, compass, ship, ammo, port, mapScale   #access the public variable
    global SCREENRECT
    global topScores
    pygame.init()       #initialise game
    clock = pygame.time.Clock()
    random.seed()       #randomise
    gameStarted = 0
    userCmds = []
    topScores = []
    myScore = 0
    

    #setup console
    #os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.display.set_caption(TITLE)
    #pygame.mouse.set_visible(0)
    screen = pygame.display.set_mode((SCREENRECT.width+CONSOLE_WIDTH,SCREENRECT.height), 0)
    #screen = pygame.display.set_mode((SCREENRECT.width,SCREENRECT.height))
    SCREEN_HEIGHT = screen.get_height()    #remember new dims
    SCREEN_WIDTH = screen.get_width() - CONSOLE_WIDTH    #remember new dims
    SCREENRECT = Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)   #game & console size


    #load resources
    Res.splash = load_image('splash.jpg', 0)
    Res.sunk = load_image('sunk.jpg', 0)
    Res.wreck = load_image('wreck.jpg', 0)
    Res.fail = load_image('fail.jpg', 0)
    Res.bg = load_image('water2.jpg', 0)
    Res.sharkfood = load_image('sharkfood.png', 1)
    Res.compassRose = load_image('rose2.png', 1)
    Res.ship = load_image('ship3.png', 1)
    Res.iceberg = load_image('iceberg2.png', 1)
    Res.island = load_image('island.png', 1)
    Res.shark = load_image('shark.png', 1)
    Res.icon = load_image('icon.jpg', 1)
    Res.wrong = load_image('wrong.png', 1)
    Res.correct = load_image('correct.png', 1)
    Res.port = load_image('anchor2.png', 1)


    #resize images
    Res.splash = pygame.transform.scale(Res.splash, scale_img(Res.splash, 0))
    Res.fail = pygame.transform.scale(Res.fail, scale_img(Res.fail))
    Res.wreck = pygame.transform.scale(Res.wreck, scale_img(Res.wreck))
    Res.sunk = pygame.transform.scale(Res.sunk, scale_img(Res.sunk))
    Res.compassRose = pygame.transform.scale(Res.compassRose, (100,100))
    Res.island = pygame.transform.scale(Res.island, (60, 68))
    Res.iceberg = pygame.transform.scale(Res.iceberg, (100, 60))
    Res.shark = pygame.transform.scale(Res.shark, (80, 35))
    Res.icon = pygame.transform.scale(Res.icon, (32, 32))
    Res.ship = pygame.transform.scale(Res.ship, (21,90))
    #Res.port = pygame.transform.scale(Res.port, (71,80))


    #initialize actors
    ship = Ship()
    compass = CompassRose()
    obstacles = []
    ammo = []
    cmdWin = CmdWin(screen)
    port = Port()
    mapScale = MapScale()
    

    #load splash screen
    pygame.display.set_icon(Res.icon)
    screen.blit(Res.splash, ((SCREEN_WIDTH/2)-(Res.splash.get_width()/2),(SCREEN_HEIGHT/2)-(Res.splash.get_height()/2)))
    load_screen(screen, '( loading . . . )', (200, 200, 200), footer="(c) 2018 Owen Jeffreys")
    ms = pygame.time.get_ticks()
    
    #list top scores
    cmdWin.write(screen, "Top Scores:", col=GREEN)
	#if not exist, then create it
    scores = open(scoreFile, "a")
    scores.close()
    with open(scoreFile, 'r') as scores:
        for line in scores:
            if len(line) > 2:
			    line = line.replace("\r\n","").split("@")
			    topScores.append([int(line[1]), line[0]])

    topScores = sorted(topScores, key=operator.itemgetter(0), reverse=True)
    results = 0
    for score in topScores:
        cmdWin.write(screen, score[1] + "  " + str(score[0]))
		#only show top 5 scores
        results = results + 1
        if results >= 5:
            break

    #add obstacles without overlap
    i=0    #number of added obstacles
    while (i < MAX_SHARKS):
        ob = Shark()
        if ob.rect.collidelist(obstacles + [ship]) == -1:
            obstacles.append(ob)
            i=i+1

    i=0    #number of added obstacles
    while (i < MAX_ICEBERGS):
        ob = Iceberg()
        if ob.rect.collidelist(obstacles + [ship]) == -1:
            obstacles.append(ob)
            i=i+1            
        
    i=0     #number of added obstacles
    while (i < MAX_ISLANDS):
        ob = Island()
        if ob.rect.collidelist(obstacles + [ship]) == -1:
            obstacles.append(ob)
            i=i+1
    
    
    #tile the background     
    bgSurf = pygame.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, Res.bg.get_width()):
        bgSurf.blit(Res.bg, (x, 0))
    screen.blit(bgSurf, (0,0))
    #screen.blit(Res.bg, (0,0))
    #cmdWin.clear(screen)


    #display actors
    for actor in obstacles + [compass] + [ship] + [port]:
        actor.draw(screen)

    mapScale.draw(screen, bgSurf)
    
    ms = pygame.time.get_ticks() - ms
    if ms < SPLASH_DISPLAY:
        pygame.time.wait(SPLASH_DISPLAY - ms)
        
    pygame.display.flip()

    
    #read user ship commands
    cmd = ""
    name = ""
    msgOK = "Aye aye, Captain!"
    msgERR = "I don't understand!"
    esc = 0
    
	#clear top scores
    cmdWin.clear(screen)
    cmdWin.write(screen, 'Captain: ', 0)
    startTime = pygame.time.get_ticks()

    #listen for cmds loop
    while not gameStarted and not esc:
        clock.tick(FRAMES_PER_SEC)  #cap fps
        
        clear_actors(screen, bgSurf)
        refresh_actors(screen, bgSurf)
        
        for evt in pygame.event.get():
            if evt.type == QUIT:
                esc = 1
                break
            elif evt.type == KEYDOWN:
                if evt.key == K_BACKSPACE:
                    cmd = cmd[:-1]
                    cmdWin.write(screen, cmd, 0)
                    
                elif evt.key == K_ESCAPE:
                    esc = 1
                    break
                
                elif evt.key == K_RETURN:
                    cmdWin.write(screen, cmd)
                    cmdList = cmd.split(" ")

                    if name == "":  #setting the captain name
                        if cmd != "":
                            name = cmd
                            cmdWin.write(screen, "Ship: ", 0)
                        else:
                            cmdWin.write(screen, "Captain: ", 0)
                    else:   #entering a ship command
                        if len(cmdList) == 2:
                            if cmdList[0] in shipCmds and cmdList[1].isdigit():
                                userCmds.append(cmdList)
                                cmdWin.write(screen, msgOK, col=GREEN)
                            else:
                                cmdWin.write(screen, msgERR, col=RED)
                        elif cmd == shipCmds[3]:    #sos
                            userCmds.append(cmdList)
                            cmdWin.write(screen, msgOK, col=GREEN)
                        elif cmd == shipCmds[0]:    #start
                            userCmds.append(cmdList)
                            cmdWin.write(screen, "Anchors away!", col=BLUE)
                            gameStarted = 1
                            break
                        else:
                            cmdWin.write(screen, msgERR, col=RED)

                        cmdWin.write(screen, "Ship: ", 0)
                            
                    cmd=""
                    
                elif evt.key <= 127:
                    cmd += chr(evt.key)     #.unicode
                    cmdWin.write(screen, cmd, 0)

        
    
##    while cmd != shipCmds[0]:
##        cmd = raw_input('ship: ')
##        cmdList = cmd.split(" ")
##        
##        if len(cmdList) == 2:
##            if cmdList[0] in shipCmds and cmdList[1].isdigit():
##                userCmds.append(cmdList)
##                print msgOK
##            else:
##                print msgERR
##        elif cmdList[0] == shipCmds[3]:
##            userCmds.append(cmdList)
##            print msgOK
##        elif cmdList[0] == shipCmds[0]:
##            userCmds.append(cmdList)
##            print "Anchors away!\n"
##        else:
##            print msgERR

    

    #start score table entry if name exists
    if len(name) > 0:
        scores = open(scoreFile, "a")
        scores.write(name + "@")
        scores.close()


    #main game loop
    while 1:
        if esc: break   #user wishes to quit
        
        clock.tick(FRAMES_PER_SEC)  #don't run too fast
        

        #read inputs and check for exit
        pygame.event.pump()
        keystate = pygame.key.get_pressed()
        if keystate[K_ESCAPE] or pygame.event.peek(QUIT):
            break


        #check for obstacles collision
        i = ship.rect.collidelist(obstacles)
        if gameStarted and i != -1:
            if obstacles[i].isShark: collision(Res.fail, screen)
            elif obstacles[i].isIceberg: collision(Res.sunk, screen)
            elif obstacles[i].isIsland: collision(Res.wreck, screen)
            break


        #check for arrival at destination
        if gameStarted and ship.rect.colliderect(port):
            endTime = pygame.time.get_ticks()
            allowedTime = (60000 * 1.5) #1.5 minutes
            timeTaken = (endTime - startTime)
            myScore = int((allowedTime - timeTaken) / 1000)
            mission_completed(screen)
            break


        #check for shark food collision
        for a in ammo:
            i = a.rect.collidelist(obstacles)
            try:
                if i != -1 and i.isShark:   #if hit object and is shark
                    del obstacles[i]    #remove shark
                    break
            except:
                pass

        
        clear_actors(screen, bgSurf)    #take images of screen

        #move the ship
        if len(userCmds) > 0: #commands left to execute
            if userCmds[0][0] == shipCmds[1]:   #move
                if userCmds[0][1] > 0:
                    ship.move(SHIP_SPEED)
                    userCmds[0][1] = int(userCmds[0][1]) - 1
                else:
                    del userCmds[0]
            elif userCmds[0][0] == shipCmds[2]:   #turn
                if userCmds[0][1] > 0:
                    #ship.turn(SHIP_SPEED)
                    #userCmds[0][1] = int(userCmds[0][1]) - SHIP_SPEED
                    ship.turn(int(userCmds[0][1]))
                    del userCmds[0]
                else:
                    del userCmds[0]
            elif userCmds[0][0] == shipCmds[3]:   #sos cmd (attack shark)
                ammo.append(SharkFood((ship.rect.centerx, ship.rect.centery)))
            elif userCmds[0][0] == shipCmds[0]:   #start (last command)
                gameStarted = 0
                break

        refresh_actors(screen, bgSurf)  #put images back on screen in new positions


    if not gameStarted: mission_failed(screen)
    
    if len(name) > 0:
        scores = open(scoreFile, "a")
        scores.write(str(myScore) + "\r\n")
        scores.close()

    pygame.time.wait(SPLASH_DISPLAY)
    if not esc: main()
    else: pygame.quit()



if __name__ == '__main__': main()
