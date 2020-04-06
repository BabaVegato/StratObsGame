import pygame
import client
import server
import threading
import socket
import time
import ipaddress
from communication import *

pygame.init()

#Polices
pygame.font.init()
fontBtn = pygame.font.Font("media\BlackOpsOne-Regular.ttf",25) #Police à changer
fontTitle = pygame.font.Font("media\BlackOpsOne-Regular.ttf",100)
font = pygame.font.Font("media\BlackOpsOne-Regular.ttf",30)
font2 = pygame.font.Font("media\BlackOpsOne-Regular.ttf",20)

#Constantes
GRIS = (169,169,169)
BLANC = (255,255,255)
NOIR = (0,0,0)
DARK_GREY = (45,36,30)
DARK_GREEN = (9,82,40)
RED = (190,0,0)
GREEN = (107,142,35)
GREY = (105,105,105)

#Dimensions écran
winWidth = 1300
winHeight = 750

#Grille
grid = [[None,None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None,None]]

win = pygame.display.set_mode((winWidth, winHeight))

pygame.display.set_caption("First Game")
clock = pygame.time.Clock()

is_time_passed = False
sound_played = False

class case(object):
    def __init__(self, width, height, nbX, nbY):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.gap = 3
        self.mapWidth = nbX*self.width+(nbX-1)*self.gap
        self.offsetX = (winWidth-self.mapWidth)//2 #Centrer la grille
        self.offsetY = (winHeight-(nbY*self.height+(nbY-1)*self.gap))//2
        self.gridHitbox = (self.offsetX-self.gap, self.offsetY-self.gap, self.mapWidth+2*self.gap, nbY*self.height+(nbY-1)*self.gap+2*self.gap)
    def draw(self, win):
        hitbox = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(win, GRIS, hitbox)

class case2(object):
    def __init__(self, i, j):
        self.highlighted = False #sélectionnée
        #Caractéristique unité
        self.unit1 = ""
        self.unit1_moved = False
        self.moving = False
        self.remaining_moves = 2
        self.unit_observing = False
        ######################
        self.observed = False
        self.reachable = False
        self.col = j
        self.lig = i
        self.type = "case"
        self.id = (i,j)
        self.lignes = 11
        self.colonnes = 9
        self.width = 50
        self.height = 50
        self.gap = 3
        self.mapWidth = self.colonnes*self.width+(self.colonnes-1)*self.gap
        self.offsetX = (winWidth-self.mapWidth)//2
        self.offsetY = (winHeight-(self.lignes*self.height+(self.lignes-1)*self.gap))//2
        self.x = self.offsetX + j*(self.width + self.gap)
        self.y = self.y = self.offsetY + i*(self.height + self.gap)
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.xMax = self.x + self.width
        self.yMax = self.y + self.height
        self.wall = False
    def draw(self, win):
        if self.wall :
            pygame.draw.rect(win, DARK_GREY, self.hitbox)
        else:
            if self.reachable:
                color_case = GREEN 
            elif self.observed:
                color_case = GRIS
            else:
                color_case = GREY
            pygame.draw.rect(win, color_case, self.hitbox)
            if self.unit1 != "":
                if self.unit1 == "soldier":
                    pygame.draw.rect(win, RED, (self.x+(self.width-20)//2,self.y+(self.width-20)//2,20,20))
                if self.highlighted:
                    pygame.draw.rect(win, DARK_GREY, (self.x + (self.width-40)//2, self.y + (self.height-40)//2, 40, 40), 3)

class button(object):
    def __init__(self, x, y, width, height, id, text):
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.xMax = self.x + self.width
        self.yMax = self.y + self.height
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.posText = (self.x+5, int(self.y+self.height/4)+5) #à améliorer
    def draw(self, win):
        text = fontBtn.render(self.text, False, (240,240,240))
        pygame.draw.rect(win, DARK_GREY, self.hitbox)
        win.blit(text, self.posText)

class button2(object):
    def __init__(self, x, y, id, text):
        paddingX = 6
        paddingY = 0
        self.type = "button"
        self.x = x
        self.y = y
        self.id = id
        self.text = fontBtn.render(text, False, (240,240,240))
        self.x_text = x + paddingX
        self.y_text = y + paddingY
        self.pos_text = (self.x_text, self.y_text)
        self.width = self.text.get_width() + 2*paddingX
        self.height = self.text.get_height() + 2*paddingY
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.xMax = self.x + self.width
        self.yMax = self.y + self.height
    def draw(self, win):
        pygame.draw.rect(win,DARK_GREY,self.hitbox)
        win.blit(self.text, self.pos_text)

class obstacle(object):
    def __init__(self, x, y, shape, id, case):
        self.placed = False
        self.type = "obstacle"
        self.x = x
        self.y = y
        self.shape = shape
        self.id = id
        self.case = case
        self.selected = False
        if shape == "h":
            self.width = self.case.width*2+self.case.gap
            self.height = self.case.height
        elif shape == "v":
            self.width = self.case.width
            self.height = self.case.height*2+self.case.gap
        elif shape == "p":
            self.width = self.case.width
            self.height = self.case.height
        elif shape == "t":
            self.width = self.case.width*3+self.case.gap*2
            self.height = 2*self.case.height+self.case.gap
        self.xMax = x + self.width
        self.yMax = y + self.height
    def draw(self,win):
        if not(self.selected):
            x = self.x 
            y = self.y
        else :
            mouseX, mouseY = pygame.mouse.get_pos()
            x = mouseX - self.case.width//2
            y = mouseY - self.case.height//2
        hitbox = (x, y, self.width, self.height)
        hitboxT1 = (x, y, self.case.width*3+self.case.gap*2, self.case.height+self.case.gap)
        hitboxT2 = (x+self.case.width+self.case.gap, y+self.case.height+self.case.gap, self.case.width+self.case.gap, self.case.height+self.case.gap)
        if not(self.placed):
            if self.shape == "t":
                pygame.draw.rect(win, DARK_GREY, hitboxT1)
                pygame.draw.rect(win, DARK_GREY, hitboxT2)
            else :
                pygame.draw.rect(win, DARK_GREY, hitbox)

class soldier(object):
    def __init__(self, x, y):
        self.selected = False #Drag'n drop
        self.classe = "soldier"
        self.type = "unit"
        self.selected = False
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.xMax = x + self.width
        self.yMax = y + self.height
        self.hitbox = (self.x, self.y, self.width, self.height)
    def draw(self,win):
        pygame.draw.rect(win, RED, self.hitbox)
        if self.selected :
            x,y = pygame.mouse.get_pos()
            hitbox = (x-self.width//2,y-self.height//2,self.width, self.height)
            pygame.draw.rect(win, RED, hitbox)

#Cases :
case = case(50,50,9,11)
for i in range(11):
    for j in range(9):
        grid[i][j] = case2(i,j)

#Boutons :
butHeight1 = 100
butWidth1 = 300
btnCreate = button(int(winWidth/2-butWidth1/2), int(winHeight/3), butWidth1, butHeight1, "btnCreate", "Créer une partie")
btnJoin = button(int(winWidth/2-butWidth1/2), int(winHeight*2/3), butWidth1, butHeight1, "btnJoin", "Rejoindre une partie")
btn_move = button2(case.offsetX + case.mapWidth + 2*case.width,case.offsetY + case.height,"btn_move", "MOVE")
btn_obs = button2(case.offsetX + case.mapWidth + 2*case.width,case.offsetY + 2*case.height,"btn_obs","OBSERVE")
btn_atk = button2(case.offsetX + case.mapWidth + 2*case.width,case.offsetY + 3*case.height,"btn_atk","SHOOT")
list_but = [btn_move, btn_obs, btn_atk]

#Obstacles :
obsV1 = obstacle((case.offsetX-3*case.height)//4,case.offsetY+case.height+case.gap,"v","obsV1",case)
obsV2 = obstacle(2*(case.offsetX-3*case.height)//4+case.height,case.offsetY+case.height+case.gap,"v","obsV2",case)
obsV3 = obstacle(3*(case.offsetX-3*case.height)//4+2*case.height,case.offsetY+case.height+case.gap,"v","obsV3",case)
obsH1 = obstacle((case.offsetX-3*case.height)//4,case.offsetY+4*case.height+5*case.gap,"h","obsH1",case)
obsH2 = obstacle((case.offsetX-3*case.height)//4,case.offsetY+6*case.height+7*case.gap,"h","obsH2",case)
obsH3 = obstacle((case.offsetX-3*case.height)//4,case.offsetY+8*case.height+9*case.gap,"h","obsH3",case)
obsP1 = obstacle((case.offsetX-3*case.height)//4+3*case.height,case.offsetY+4*case.height+5*case.gap,"p","obsP1",case)
obsP2 = obstacle((case.offsetX-3*case.height)//4+5*case.height,case.offsetY+4*case.height+5*case.gap,"p","obsP2",case)
obsP3 = obstacle((case.offsetX-3*case.height)//4+4*case.height,case.offsetY+6*case.height+7*case.gap,"p","obsP3",case)
obsT = obstacle((case.offsetX-3*case.height)//4+3*case.height,case.offsetY+8*case.height+9*case.gap,"t","obsT",case)
listObs = [obsV1, obsV2, obsV3, obsH1, obsH2, obsH3, obsP1, obsP2, obsP3, obsT]

#Units :
soldier = soldier(case.offsetX+case.mapWidth+3*case.width,case.offsetY+2*case.height)
listUnit = [soldier]

def pass_time(seconds):
    time.sleep(seconds) #Y'avait autre chose mais jsplus quoi et ça marche alors bon........
    global is_time_passed
    is_time_passed = True

def display_obstacles():
    for obs in listObs:
        obs.draw(win)

def display_grid():
    pygame.draw.rect(win, DARK_GREY, case.gridHitbox)
    for i in range(11):
        for j in range(9):
            grid[i][j].draw(win)

def find_selected_unit():
    for i in range(11):
        for j in range(9):
            if grid[i][j].highlighted:
                return grid[i][j]
    return None

def display_but():
    for but in list_but:
        but.draw(win)

def display_text(state, turn, id_player, nb_unit):
    if state == "map creation":
        if turn == id_player :
            text_turn = font.render("Your turn to place", True, (0, 128, 0))
        else :
            text_turn = font.render("Waiting for your opponent", True, (0, 128, 0))

        text = font.render("Create the map", True, (0, 128, 0))
        win.blit(text,(winWidth//2 - text.get_width() // 2, winHeight//20 - text.get_height() // 2))
        win.blit(text_turn,(winWidth//2 - text.get_width() // 2, int(winHeight//20 + 0.8*text.get_height() // 2)))
        text = font2.render("Obstacles", True, DARK_GREEN)
        win.blit(text,(case.offsetX//2-text.get_width()//2, winHeight//14 - text.get_height() // 2))
    elif state == "units placement":
        text = font.render("Place your units", True, (0, 128, 0))
        win.blit(text,(winWidth//2 - text.get_width() // 2, winHeight//20 - text.get_height() // 2))
        text = font2.render("Units", True, DARK_GREEN)
        win.blit(text,(case.offsetX//2+case.offsetX+case.mapWidth-text.get_width()//2, winHeight//14 - text.get_height() // 2))
        text = font2.render("Remaining : "+str(nb_unit), True, NOIR)
        win.blit(text,(case.offsetX+case.mapWidth+case.width, case.offsetY+case.height))
        text = font2.render("Soldier :", True, NOIR)
        win.blit(text,(case.offsetX+case.mapWidth+case.width, case.offsetY+2*case.height))
    elif state == "game":
        if turn == id_player:
            text = font.render("Your turn", True, (0, 128, 0))
            win.blit(text,(winWidth//2 - text.get_width() // 2, winHeight//20 - text.get_height() // 2))
            selected_unit = find_selected_unit()
            if selected_unit != None:
                text = font2.render("Actions", True, DARK_GREEN)
                win.blit(text,(case.offsetX//2+case.offsetX+case.mapWidth-text.get_width()//2, winHeight//14 - text.get_height() // 2))
                display_but()
        else :
            text = font.render("Opponent's turn", True, (0, 128, 0))
            win.blit(text,(winWidth//2 - text.get_width() // 2, winHeight//20 - text.get_height() // 2))

def display_unit():
    soldier.draw(win)

def redraw_window(state, turn, id_player, nb_unit):
    if state == "entry" :
        win.fill((255, 255, 255))
        title = fontTitle.render("StratObsGame", False, (0,0,0))
        win.blit(title, (int(winWidth/5+25),50)) #not responsive
        btnCreate.draw(win)
        btnJoin.draw(win)
        pygame.display.update()

    elif state == "waiting for connexion" :
        win.fill((240, 240, 240))
        text_wait = font.render("Waiting for a connexion", True, (0, 128, 0))
        text_dot = font.render("...", True, (0, 128, 0))
        win.blit(text_wait,(int(winWidth//2 - text_wait.get_width() // 2), int(winHeight//2 - text_wait.get_height() // 2)))
        win.blit(text_dot,(int(winWidth//2 - text_dot.get_width() // 2), int(winHeight//2 - text_dot.get_height() // 2 + text_wait.get_height())))
        pygame.display.update()

    elif state == "connexion established":
        win.fill((240, 240, 240))
        text = font.render("Connexion established !", True, (0, 128, 0))
        win.blit(text,(int(winWidth//2 - text.get_width() // 2), int(winHeight//2 - text.get_height() // 2)))
        pygame.display.update()
        
    elif state =="map creation":
        win.fill((240, 240, 240))
        display_text(state , turn, id_player, nb_unit)
        display_grid()
        display_obstacles()
        pygame.display.update()
    
    elif state == "units placement":
        win.fill((240,240,240))
        display_text(state,turn, id_player, nb_unit)
        display_grid()
        display_unit()
        pygame.display.update()
    
    elif state == "game":
        win.fill((240,240,240))
        display_text(state,turn,id_player,nb_unit)
        display_grid()
        pygame.display.update()

def pointed(obj):
    xMouse, yMouse = pygame.mouse.get_pos()
    if xMouse < obj.xMax and xMouse > obj.x and yMouse < obj.yMax and yMouse > obj.y:
        return True
    else :
        return False

def check_placement(obj, case):
    if obj.type == "obstacle":
        if obj.shape == "h":
            if not(case.col == 8) and not(case.wall) and not(grid[case.lig][case.col+1].wall) :
                return True
        elif obj.shape == "v":
            if not(case.lig == 10) and not(case.wall) and not(grid[case.lig+1][case.col].wall):
                return True
        elif obj.shape == "p" and not(case.wall):
            return True
        elif obj.shape == "t":
            if not(case.col == 8 or case.col == 7 or case.lig == 10) and not(case.wall or grid[case.lig][case.col+1].wall or grid[case.lig][case.col+2].wall or grid[case.lig+1][case.col+1].wall) :
                return True
    elif obj.type == "unit":
        if obj.classe == "soldier":
            if not(case.wall) and case.unit1 == "":
                return True
    else:
        return False

def place_obs(obs, case):
    if obs.shape == "h":
        case.wall = True
        grid[case.lig][case.col+1].wall = True
    elif obs.shape == "v":
        case.wall = True
        grid[case.lig+1][case.col].wall = True
    elif obs.shape == "p":
        case.wall = True
    elif obs.shape == "t":
        case.wall = True
        grid[case.lig][case.col+1].wall = True
        grid[case.lig][case.col+2].wall = True
        grid[case.lig+1][case.col+1].wall = True
    obs.placed = True

def placeUnit(unit, case):
    if unit.classe == "soldier":
        case.unit1 = "soldier"

def identify_obs(id):
    for obs in listObs:
        if obs.id == id:
            return obs

def identify_case(id):
    for i in range(11):
        for j in range(9):
            if grid[i][j].id == id:
                return grid[i][j]

def apply_modif(modif):
    obs = identify_obs(modif[0])
    case = identify_case(modif[1])
    if obs != None and case != None:
        place_obs(obs, case)

def reset_reach():
    for i in range(11):
        for j in range(9):
            if grid[i][j].reachable:
                grid[i][j].reachable = False

def moving(unit): 
    if unit.remaining_moves != 0:
        unit.moving = True
        for i in range(11):
            for j in range(9):
                ie = abs(i-unit.lig)
                je = abs(j-unit.col)
                if abs(ie+je) <= unit.remaining_moves and not(grid[i][j].wall) and grid[i][j].unit1 == "":
                    grid[i][j].reachable = True

def check_movement(case):
    if case.reachable:
        return True
    else:
        return False

def move_unit(unit,case):
    case.unit1 = unit.unit1
    unit.unit1 = ""
    case.remaining_moves = unit.remaining_moves
    unit.remaining_moves = 2
    unit.moving = False
    case.moving = False
    mov = abs(abs(case.lig-unit.lig)+abs(case.col-unit.col))
    case.remaining_moves-=mov
    if case.remaining_moves == 0:
        case.unit1_moved = True
    unit.highlighted = False
    case.highlighted = True
    reset_reach()

def disable_moving(selected_unit):
    selected_unit.moving = False
    reset_reach()
    return False

def observe(unit): #évalue chaque direction à partir de la case
    i,j = unit.id
    stop = False
    for io in range(i,11): #Bas
        case = grid[io][j]
        if not(case.wall) and not(case.observed) and not(stop):
            case.observed = True
        elif case.wall:
            stop = True
    stop = False
    for io in range(-i,1): #Haut
        case = grid[-io][j]
        if not(case.wall) and not(case.observed) and not(stop):
            case.observed = True
        elif case.wall:
            stop = True    
    stop = False
    for jo in range(j,9): #Droite
        case = grid[i][jo]
        if not(case.wall) and not(case.observed) and not(stop):
            case.observed = True
        elif case.wall:
            stop = True 
    stop = False
    for jo in range(-j,1): #Gauche
        case = grid[i][-jo]
        if not(case.wall) and not(case.observed) and not(stop):
            case.observed = True
        elif case.wall:
            stop = True 
    case.unit_observing = True
    case.unit1_moved = True

    return unit.id

def play_sound(sound):
    global sound_played
    if sound_played == False :
        pygame.mixer.music.load(f'media\{sound}.wav')
        pygame.mixer.music.play(0)
        sound_played = True


def main():
    state = "entry"
    thr_created_conn_esta = False
    run = True
    serv = None
    cli = None
    mouse = "" #l'objet que pointe la souris
    clic = False #Limiter à un clic
    info_sent = False
    selected = False
    selected_obs = ""
    nb_unit = 8
    modif = None, None
    ready_to_play = False
    other_ready_to_play = False
    other_really_ready = False
    idUnitObs = (0, 0)
    turn = 0
    id_player = 0
    sound_played = False
    casesObserv = []
    #highlighting_mode = False #Les cases sont surlignées au passage de la souris
    moving_unit = False

    ######### TEST ############
    grid[0][0].unit1 = "soldier"
    ###########################

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit")
                if serv != None :
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((host, port))
                run = False
                quit()
        if state == "entry" :
            #Test position souris
            if pointed(btnCreate) :
                mouse = btnCreate.id
            elif pointed(btnJoin) :
                mouse = btnJoin.id
            else :
                mouse = ""
            #Clic bouton
            if pygame.mouse.get_pressed()[0]: #Si clic gauche
                if mouse == btnCreate.id and not(clic):
                    clic = True
                    serv = launch_server(state)
                    state = "waiting for connexion"
                    serv_wait = threading.Thread(target=serv.wait_for_object, args=[serv.conn])
                    serv_wait.daemon = True
                    serv_wait.start()
                    info_sent = False

                if mouse == btnJoin.id and not(clic):
                    clic = True
                    cli = client.Client()
                    cli.create_client(host, port)
                    cli_wait = threading.Thread(target=cli.wait_for_object)
                    cli_wait.daemon = True
                    cli_wait.start()
                    id_player = 1 # le client est le 2e joueur
                    info_sent = False
            else :
                clic = False
                
        elif state == "waiting for connexion" :
            play_sound('modem')

            if serv.conn_addr != None :
                pygame.mixer.music.stop()
                state = "connexion established"
                info_sent = False

        elif state == "connexion established":
            play_sound('log')
            if not thr_created_conn_esta :
                thread_pass_time = threading.Thread(target=pass_time, args=[3])
                thread_pass_time.daemon = True
                thread_pass_time.start()
                thr_created_conn_esta = True
            global is_time_passed
            if is_time_passed :
                state = "map creation"
                info_sent = False

        elif (state == "map creation") & (turn == id_player):
            nb_obs_mis_total = 0
            for obs in listObs :
                if obs.placed :
                    nb_obs_mis_total+=1
            if nb_obs_mis_total == len(listObs) :
                state = "units placement"
                info_sent = False

            #Test position souris
            mouse = ""
            for obs in listObs:
                if pointed(obs):
                    mouse = obs
            for i in range(11):
                for j in range(9):
                    if pointed(grid[i][j]):
                        mouse = grid[i][j]
                
            if pygame.mouse.get_pressed()[0]:
                if mouse != "" and not(clic) and not(selected): #On est sur un objet et rien n'est sélectionné
                    if mouse.type == "obstacle" and not(mouse.placed): #On sélectionne l'obstacle
                        clic = True
                        mouse.selected = True
                        selected = True
                        selected_obs = mouse
                    elif mouse.type == "case": #Osef
                        clic = True
                elif selected and not(clic) and mouse != "": #On est sur un objet et un obstacle est sélectionné
                    clic = True
                    if mouse.type == "case": #On clique sur une case
                        if(check_placement(selected_obs, mouse)):
                            place_obs(selected_obs, mouse)
                            selected_obs.selected = False
                            selected = False
                            modif = selected_obs.id, mouse.id
                            
                            turn+=1
                            if turn == 2 : turn = 0
                            
                            info_sent = False

                elif not(clic) and selected: #Si on clique autrepart que sur une case
                    selected_obs.selected = False
                    selected = False
            else :
                clic = False

        elif state == "units placement":   
            if ((other_really_ready == True) & (ready_to_play == True) & (serv != None)):
                print("go to game")
                state = "game"
                info_sent = False
            mouse = ""
            for unit in listUnit:
                if pointed(unit):
                    mouse = unit
            for i in range(11):
                for j in range(9):
                    if pointed(grid[i][j]):
                        mouse = grid[i][j]
            
            if pygame.mouse.get_pressed()[0]:
                if mouse != "" and not(clic) and not(selected) and nb_unit > 0:
                    if mouse.type == "unit": #On sélectionne l'unité
                        clic = True
                        mouse.selected = True
                        selected = True
                        selected_unit = mouse
                        selected_unit.selected = True
                        print(mouse.classe)
                elif selected and not(clic) and mouse != "": #On est sur un objet et une unité est sélectionnée
                    clic = True
                    if mouse.type == "case": #On clique sur une case
                        if(check_placement(selected_unit, mouse)):
                            placeUnit(selected_unit, mouse)
                            selected_unit.selected = False
                            selected = False
                            nb_unit -= 1
                            if nb_unit == 0:
                                ready_to_play = True
                                if(serv == None):
                                    info_sent = False
                elif not(clic) and selected: #Si on clique autrepart que sur une case
                    selected_unit.selected = False
                    selected = False

            else:
                clic = False
        
        elif state == "game":
            mouse = ""
            for i in range(11):
                for j in range(9):
                    if pointed(grid[i][j]):
                        mouse = grid[i][j]
            for i in list_but:
                if pointed(i):
                    mouse = i

            if pygame.mouse.get_pressed()[0]:
                if mouse != "" and not(clic) and not(selected): #Si on clique et qu'aucune unité n'est sélectionnée
                    clic = True
                    if mouse.type == "case": #Si on clique sur une case
                        if mouse.unit1 != "": #S'il y a une unité sur cette case, on la sélectionne
                            mouse.highlighted = True
                            selected_unit = mouse
                            selected = True
                elif mouse != "" and not(clic) and selected: #Si on clique et une unité est sélectionnée
                    clic = True
                    if mouse.type == "button": #Si on clique sur un bouton
                        if mouse.id == "btn_move":
                            if not(selected_unit.unit1_moved):
                                moving(selected_unit)
                                moving_unit = True
                            print("btn_move")
                        elif mouse.id == "btn_obs":
                            if moving_unit:
                                moving_unit = disable_moving(selected_unit)
                            if not(selected_unit.unit_observing) and not(selected_unit.unit1_moved):
                                idUnitObs = observe(selected_unit)
                                for rangee in grid :
                                    for case in rangee:
                                        casesObserv.append(case)
                                info_sent = False
                            print("btn_obs")
                        elif mouse.id == "btn_atk":
                            if moving_unit:
                                moving_unit = disable_moving(selected_unit)
                            print("btn_atk")
                    elif mouse.type == "case" and moving_unit: #Si on clique sur une case alors qu'une unité est en mouvement
                        if check_movement(mouse): #Si l'unité peut s'y déplacer
                            move_unit(selected_unit, mouse)
                            moving_unit = False
                            selected_unit = mouse
                    else:
                        clic = True
                        selected = False
                        selected_unit.highlighted = False
                        if moving_unit:
                            moving_unit = disable_moving(selected_unit)
                        selected_unit = None
                elif selected and not(clic): #Si on clique autre part et qu'une unité est sélectionnée, on déselectionne
                    clic = True
                    selected = False
                    selected_unit.highlighted = False
                    if moving_unit:
                        moving_unit = disable_moving(selected_unit)
                    selected_unit = None
            else :
                clic = False

        

        if(state == "game"):
            info = {"state" : state, "modif": modif, "turn": turn, "useful stuff": ready_to_play}
            info_sent, state, idUnitObs, turn, casesObserv = sending_and_receiving(serv, cli, info_sent, info, state, idUnitObs, turn, casesObserv)

        else:
            info = {"state" : state, "modif": modif, "turn": turn, "useful stuff": ready_to_play}
            info_sent, state, modif, turn, other_ready_to_play = sending_and_receiving(serv, cli, info_sent, info, state, modif, turn, ready_to_play)



        if other_ready_to_play == True:
            other_really_ready = True

        apply_modif(modif)
        redraw_window(state, turn, id_player, nb_unit)

main()
pygame.quit()
quit()