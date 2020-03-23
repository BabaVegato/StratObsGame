import pygame
import client
import server
import threading
import socket

pygame.init()

host = "192.168.1.66"
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
    if state != "waiting for connexion" :
        print("non")
        win.fill((255, 255, 255))
        btnTest1.draw(win)
        btnTest2.draw(win)
        pygame.display.update()

    elif state == "waiting for connexion" :
        print("oui")
        win.fill((100, 0, 0))
        pygame.display.update()


btnTest1 = button(200, 200, 100, 100, "btnTest1")
btnTest2 = button(400, 200, 100, 100, "btnTest2")

def launch_server(threads, state):
    if state != "waiting for connexion" :
        serv = server.Server()
        serv.create_server(host, port)
        wait = threading.Thread(target=serv.wait_for_a_connection)
        threads.append(wait)
        wait.start()
        state = "waiting for connexion"


def main():
    state = ""
    threads = [threading.Thread]
    run = True
    serv = None
    mouse = "" #l'objet que pointe la souris
    clic = False #Limiter à un clic

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit") #??????????????????????????????
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
        if pygame.mouse.get_pressed()[0]: #Si clic gauche
            if mouse == btnTest1.id and not(clic):
                clic = True
                print("Bouton server")
                launch_server(threads, state)
                state = "waiting for connexion"

            if mouse == btnTest2.id and not(clic):
                clic = True
                print("Bouton client")
                cli = client.create_client(host, port)
                client.send_obj(cli, d)
        else :
            clic = False
            
        redrawWindow(state)

main()
pygame.quit()
quit()