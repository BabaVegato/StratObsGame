import pygame
import client
import server
import threading
import socket
import time


pygame.init()

host = "192.168.1.68"
port = 5555
is_waiting_for_connexion = False

state = ""


#Dimensions écran
winWidth = 500
winHeight = 500
d = {1: winWidth, 2: winHeight}

win = pygame.display.set_mode((winWidth, winHeight))

pygame.display.set_caption("First Game")
clock = pygame.time.Clock()

def pass_time(seconds):
    time.sleep(seconds)
    return seconds

class button(object):
    def __init__(self, x, y, width, height, id):
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.xMax = self.x + self.width
        self.yMax = self.y + self.height
        self.hitbox = (self.x, self.y, self.width, self.height)
    def draw(self, win):
        pygame.draw.rect(win, (0,0,0), self.hitbox)

def redrawWindow(state):
    if state == "entry" :
        win.fill((255, 255, 255))
        btnTest1.draw(win)
        btnTest2.draw(win)
        pygame.display.update()

    elif state == "waiting for connexion" :
        win.fill((240, 240, 240))
        font = pygame.font.Font(r"C:\Users\Baptiste\Desktop\Eyes\StratObsGame\media\BlackOpsOne-Regular.ttf",30)
        text_wait = font.render("Waiting for a connexion", True, (0, 128, 0))
        text_dot = font.render("...", True, (0, 128, 0))
        win.blit(text_wait,(winWidth//2 - text_wait.get_width() // 2, winHeight//2 - text_wait.get_height() // 2))
        win.blit(text_dot,(winWidth//2 - text_dot.get_width() // 2, winHeight//2 - text_dot.get_height() // 2 + text_wait.get_height()))
        pygame.display.update()

    elif state == "connexion established":
        win.fill((240, 240, 240))
        font = pygame.font.Font(r"C:\Users\Baptiste\Desktop\Eyes\StratObsGame\media\BlackOpsOne-Regular.ttf",30)
        text = font.render("Connexion established !", True, (0, 128, 0))
        win.blit(text,(winWidth//2 - text.get_width() // 2, winHeight//2 - text.get_height() // 2))
        pygame.display.update()
    
    elif state =="map creation":
        win.fill((240, 240, 240))
        font = pygame.font.Font(r"C:\Users\Baptiste\Desktop\Eyes\StratObsGame\media\BlackOpsOne-Regular.ttf",30)
        text = font.render("Create the map", True, (0, 128, 0))
        win.blit(text,(winWidth//2 - text.get_width() // 2, winHeight//4 - text.get_height() // 2))
        pygame.display.update()


btnTest1 = button(int(winWidth/4), 200, 100, 100, "btnTest1")
btnTest2 = button(int(3*winWidth/4), 200, 100, 100, "btnTest2")

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
        if xMouse > btnTest1.x and xMouse < btnTest1.xMax and yMouse > btnTest1.y and yMouse < btnTest1.yMax :
            mouse = btnTest1.id
        elif xMouse > btnTest2.x and xMouse < btnTest2.xMax and yMouse > btnTest2.y and yMouse < btnTest2.yMax :
            mouse = btnTest2.id
        else :
            mouse = ""

        #Clic bouton
        if state == "entry" :
            if pygame.mouse.get_pressed()[0]: #Si clic gauche
                if mouse == btnTest1.id and not(clic):
                    clic = True
                    print("Bouton server")
                    serv = launch_server(state)
                    state = "waiting for connexion"
                    info_sent = False

                if mouse == btnTest2.id and not(clic):
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