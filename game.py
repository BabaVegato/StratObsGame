import pygame
import client
import server
import threading
import socket
import time
import ipaddress

pygame.init()

#Polices
pygame.font.init()
fontBtn = pygame.font.Font("media\BlackOpsOne-Regular.ttf",30) #Police à changer
fontTitle = pygame.font.Font("media\BlackOpsOne-Regular.ttf",100)
font = pygame.font.Font("media\BlackOpsOne-Regular.ttf",30)
font2 = pygame.font.Font("media\BlackOpsOne-Regular.ttf",20)

host = socket.gethostbyname(socket.gethostname())
port = 5555

#Constantes
GRIS = (169,169,169)
BLANC = (255,255,255)
NOIR = (0,0,0)
DARK_GREY = (45,36,30)
DARK_GREEN = (9,82,40)

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
        self.col = j
        self.lig = i
        self.type = "case"
        self.id = "case" + str(i) + str(j)
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
        self.posText = (self.x, self.y+self.height/4) #à améliorer
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

def pass_time(seconds):
    time.sleep(seconds) #Y'avait autre chose mais jsplus quoi et ça marche alors bon........

def displayObstacles():
    for obs in listObs:
        obs.draw(win)

def displayGrid():
    pygame.draw.rect(win, DARK_GREY, case.gridHitbox)
    for i in range(11):
        for j in range(9):
            grid[i][j].draw(win)

def displayText(state, turn):
    if state == "map creation":
        if turn == 1 :
            text_turn = font.render("Your turn to place", True, (0, 128, 0))
        else :
            text_turn = font.render("Waiting for your opponent", True, (0, 128, 0))

        text = font.render("Create the map", True, (0, 128, 0))
        win.blit(text,(winWidth//2 - text.get_width() // 2, winHeight//20 - text.get_height() // 2))
        win.blit(text_turn,(winWidth//2 - text.get_width() // 2, winHeight//20 - 2*text.get_height() // 2))
        text = font2.render("Obstacles", True, DARK_GREEN)
        win.blit(text,(case.offsetX//2-text.get_width()//2, winHeight//14 - text.get_height() // 2))
        text = font2.render("Units", True, DARK_GREEN)
        win.blit(text,(case.offsetX//2+case.offsetX+case.mapWidth-text.get_width()//2, winHeight//14 - text.get_height() // 2))


def redrawWindow(state, turn):
    if state == "entry" :
        win.fill((255, 255, 255))
        title = fontTitle.render("StratObsGame", False, (0,0,0))
        win.blit(title, (winWidth/5+25,50)) #not responsive
        btnCreate.draw(win)
        btnJoin.draw(win)
        pygame.display.update()

    elif state == "waiting for connexion" :
        win.fill((240, 240, 240))
        text_wait = font.render("Waiting for a connexion", True, (0, 128, 0))
        text_dot = font.render("...", True, (0, 128, 0))
        win.blit(text_wait,(winWidth//2 - text_wait.get_width() // 2, winHeight//2 - text_wait.get_height() // 2))
        win.blit(text_dot,(winWidth//2 - text_dot.get_width() // 2, winHeight//2 - text_dot.get_height() // 2 + text_wait.get_height()))
        pygame.display.update()

    elif state == "connexion established":
        win.fill((240, 240, 240))
        text = font.render("Connexion established !", True, (0, 128, 0))
        win.blit(text,(winWidth//2 - text.get_width() // 2, winHeight//2 - text.get_height() // 2))
        pygame.display.update()
        pass_time(3)
    
    elif state =="map creation":
        win.fill((240, 240, 240))
        displayText(state , turn)
        displayGrid()
        displayObstacles()
        pygame.display.update()

def launch_server(state):
    serv = server.Server()
    serv.create_server(host, port)
    threading.Thread(target=serv.wait_for_a_connection).start()
    return serv

def adapt_to_server(cli, state, modif, adv_turn):
    if cli.state_rcvd != None :
        state = cli.state_rcvd.get(1)
        modif = cli.state_rcvd.get(2)
        adv_turn = cli.state_rcvd.get(3)
        cli.state_rcvd = None
    return state, modif, adv_turn

def pointed(obj):
    xMouse, yMouse = pygame.mouse.get_pos()
    if xMouse < obj.xMax and xMouse > obj.x and yMouse < obj.yMax and yMouse > obj.y:
        return True
    else :
        return False

def checkPlacement(obs, case):
    if obs.shape == "h":
        if not(case.col == 8) and not(case.wall) and not(grid[case.lig][case.col+1].wall) :
            return True
    elif obs.shape == "v":
        if not(case.lig == 10) and not(case.wall) and not(grid[case.lig+1][case.col].wall):
            return True
    elif obs.shape == "p" and not(case.wall):
        return True
    elif obs.shape == "t":
        if not(case.col == 8 or case.col == 7 or case.lig == 10) and not(case.wall or grid[case.lig][case.col+1].wall or grid[case.lig][case.col+2].wall or grid[case.lig+1][case.col+1].wall) :
            return True
    else:
        return False

def placeObs(obs, case):
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


def main():
    state = "entry"
    run = True
    serv = None
    cli = None
    mouse = "" #l'objet que pointe la souris
    clic = False #Limiter à un clic
    info_sent = False
    selected = False
    selectedObs = ""
    modif = None, None
    turn = 1
    adv_turn = 0

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
                    print("Bouton server")
                    serv = launch_server(state)
                    state = "waiting for connexion"
                    serv_wait = threading.Thread(target=serv.wait_for_object)
                    info_sent = False

                if mouse == btnJoin.id and not(clic):
                    clic = True
                    print("Bouton client")
                    cli = client.Client()
                    cli.create_client(host, port)
                    cli_wait = threading.Thread(target=cli.wait_for_object)
                    cli_wait.daemon = True
                    cli_wait.start()
                    turn = 0 # le client est le 2e à jouer (pour l'instant)
                    info_sent = False
            else :
                clic = False
                
        elif state == "waiting for connexion" :
            if serv.conn_addr != None :
                state = "connexion established"
                info_sent = False

        elif state == "connexion established":
                state = "map creation"
                info_sent = False

        elif (state == "map creation") & (turn == 1):
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
                    if mouse.type == "obstacle": #On sélectionne l'obstacle
                        clic = True
                        mouse.selected = True
                        selected = True
                        selectedObs = mouse
                        print(mouse.id)
                    elif mouse.type == "case": #Osef
                        clic = True
                        print(mouse.id)
                elif selected and not(clic) and mouse != "": #On est sur un objet et un obstacle est sélectionné
                    clic = True
                    if mouse.type == "case": #On clique sur une case
                        if(checkPlacement(selectedObs, mouse)):
                            placeObs(selectedObs, mouse)
                            selectedObs.selected = False
                            selected = False
                            modif = selectedObs.id, mouse.id
                            info_sent = False

                elif not(clic) and selected: #Si on clique autrepart que sur une case
                    selectedObs.selected = False
                    selected = False
            else :
                clic = False

        info = {1 : state, 2: modif, 3: turn}
        if (serv != None) & (cli == None) & (not info_sent): #Si t'es le serveur et que t'envoies
            if serv.conn != None :
                serv.send_obj(serv.conn, info)
                
        info_sent = True

        if (serv == None) & (cli != None): #Si t'es client et que tu reçois
            state, modif, adv_turn = adapt_to_server(cli, state, modif, adv_turn)

        redrawWindow(state, turn)

main()
pygame.quit()
quit()