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

#Dimensions écran
winWidth = 1300
winHeight = 750

#Grille
grid = [[0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0]]

win = pygame.display.set_mode((winWidth, winHeight))

pygame.display.set_caption("First Game")
clock = pygame.time.Clock()

is_time_passed = False

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
        self.unit1 = ""
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
        if not(self.wall):
            pygame.draw.rect(win, GRIS, self.hitbox)
            if self.unit1 != "":
                if self.unit1 == "soldier":
                    pygame.draw.rect(win, RED, (self.x+(self.width-20)//2,self.y+(self.width-20)//2,20,20))
        else :
            pygame.draw.rect(win, DARK_GREY, self.hitbox)

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
        self.posText = (self.x, int(self.y+self.height/4)) #à améliorer
    def draw(self, win):
        pygame.draw.rect(win, (0,0,0), self.hitbox)
        textSurface = fontBtn.render(self.text, False, (255,255,255))
        win.blit(textSurface, self.posText)

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

#Boutons :
butHeight1 = 100
butWidth1 = 300
btnCreate = button(int(winWidth/2-butWidth1/2), int(winHeight/3), butWidth1, butHeight1, "btnCreate", "Créer une partie")
btnJoin = button(int(winWidth/2-butWidth1/2), int(winHeight*2/3), butWidth1, butHeight1, "btnJoin", "Rejoindre une partie")

#Cases :
case = case(50,50,9,11)
for i in range(11):
    for j in range(9):
        grid[i][j] = case2(i,j)

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

def displayUnit():
    soldier.draw(win)

def redrawWindow(state, turn, id_player, nb_unit):
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
        displayUnit()
        pygame.display.update()

def pointed(obj):
    xMouse, yMouse = pygame.mouse.get_pos()
    if xMouse < obj.xMax and xMouse > obj.x and yMouse < obj.yMax and yMouse > obj.y:
        return True
    else :
        return False

def checkPlacement(obj, case):
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
    turn = 0
    id_player = 0

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
            if serv.conn_addr != None :
                state = "connexion established"
                info_sent = False

        elif state == "connexion established":
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
                        if(checkPlacement(selected_obs, mouse)):
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
                        if(checkPlacement(selected_unit, mouse)):
                            placeUnit(selected_unit, mouse)
                            selected_unit.selected = False
                            selected = False
                            nb_unit -= 1
                elif not(clic) and selected: #Si on clique autrepart que sur une case
                    selected_unit.selected = False
                    selected = False
            else:
                clic = False

        info = {1 : state, 2: modif, 3: turn, 4: 0}

        info_sent, state, modif, turn, nothing = sending_and_receiving(serv, cli, info_sent, info, state, modif, turn, 0)

        apply_modif(modif)
        redrawWindow(state, turn, id_player, nb_unit)

main()
pygame.quit()
quit()