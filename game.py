import pygame
import client
import server
import threading
import socket
import time
import ipaddress

pygame.init()
pygame.font.init()
fontBtn = pygame.font.SysFont('Comic Sans MS', 30) #Police à changer
fontTitle = pygame.font.SysFont('Comic Sans MS', 100)

host = socket.gethostbyname(socket.gethostname())
port = 5555
is_waiting_for_connexion = False

state = ""



#Dimensions écran
winWidth = 1300
winHeight = 750
d = {1: winWidth, 2: winHeight}

win = pygame.display.set_mode((winWidth, winHeight))

pygame.display.set_caption("First Game")
clock = pygame.time.Clock()

def pass_time(seconds):
    time.sleep(seconds)
    return seconds

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


def redrawWindow(state):
    if state == "entry" :
        win.fill((255, 255, 255))
        title = fontTitle.render("StratObsGame", False, (0,0,0))
        win.blit(title, (winWidth/5+25,50)) #not responsive
        btnCreate.draw(win)
        btnJoin.draw(win)
        pygame.display.update()

    elif state == "waiting for connexion" :
        win.fill((240, 240, 240))
        font = pygame.font.Font("media\BlackOpsOne-Regular.ttf",30)
        text_wait = font.render("Waiting for a connexion", True, (0, 128, 0))
        text_dot = font.render("...", True, (0, 128, 0))
        win.blit(text_wait,(winWidth//2 - text_wait.get_width() // 2, winHeight//2 - text_wait.get_height() // 2))
        win.blit(text_dot,(winWidth//2 - text_dot.get_width() // 2, winHeight//2 - text_dot.get_height() // 2 + text_wait.get_height()))
        pygame.display.update()

    elif state == "connexion established":
        win.fill((240, 240, 240))
        font = pygame.font.Font("media\BlackOpsOne-Regular.ttf",30)
        text = font.render("Connexion established !", True, (0, 128, 0))
        win.blit(text,(winWidth//2 - text.get_width() // 2, winHeight//2 - text.get_height() // 2))
        pygame.display.update()
        pass_time(3)
    
    elif state =="map creation":
        win.fill((240, 240, 240))
        font = pygame.font.Font("media\BlackOpsOne-Regular.ttf",30)
        text = font.render("Map creation", True, (0, 128, 0))
        win.blit(text,(winWidth//2 - text.get_width() // 2, winHeight//4 - text.get_height() // 2))
        pygame.display.update()

#Boutons :
butHeight1 = 100
butWidth1 = 300
btnCreate = button(int(winWidth/2-butWidth1/2), int(winHeight/3), butWidth1, butHeight1, "btnCreate", "Créer une partie")
btnJoin = button(int(winWidth/2-butWidth1/2), int(winHeight*2/3), butWidth1, butHeight1, "btnJoin", "Rejoindre une partie")

def launch_server(state):
    serv = server.Server()
    serv.create_server(host, port)
    threading.Thread(target=serv.wait_for_a_connection).start()
    return serv

def adapt_to_server(cli, state):
    cli.stop_wait = True
    if cli.state_rcvd != None :
        state = cli.state_rcvd.get(1)
        cli.state_rcvd = None
        return state

def main():
    state = "entry"
    run = True
    serv = None
    cli = None
    mouse = "" #l'objet que pointe la souris
    clic = False #Limiter à un clic
    info_sent = False

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit")
                if serv != None :
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((host, port))
                run = False
                quit()
    
        #Test position souris
        xMouse, yMouse = pygame.mouse.get_pos() #Position de la souris
        if xMouse > btnCreate.x and xMouse < btnCreate.xMax and yMouse > btnCreate.y and yMouse < btnCreate.yMax :
            mouse = btnCreate.id
        elif xMouse > btnJoin.x and xMouse < btnJoin.xMax and yMouse > btnJoin.y and yMouse < btnJoin.yMax :
            mouse = btnJoin.id
        else :
            mouse = ""

        if state == "entry" :
            #Clic bouton
            if pygame.mouse.get_pressed()[0]: #Si clic gauche
                if mouse == btnCreate.id and not(clic):
                    clic = True
                    print("Bouton server")
                    serv = launch_server(state)
                    state = "waiting for connexion"
                    info_sent = False

                if mouse == btnJoin.id and not(clic):
                    clic = True
                    print("Bouton client")
                    cli = client.Client()
                    cli.create_client(host, port)
                    
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

        info = {1 : state}
        if (serv == None) & (cli != None):
            cli.stop_wait = False
            wait = threading.Thread(target=cli.wait_for_object())
            wait.start()
            

        if (serv != None) & (cli == None) & (not info_sent):
            if serv.conn != None :
                serv.send_obj(serv.conn, info)
                info_sent = True

        if (serv == None) & (cli != None):
            state = adapt_to_server(cli, state)

        redrawWindow(state)

main()
pygame.quit()
quit()