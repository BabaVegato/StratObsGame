import pygame
import client
import server
import threading
import socket

pygame.init()

host = "192.168.1.68"
port = 5555
is_waiting_for_connexion = False

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

def redrawWindow():
    if not is_waiting_for_connexion :
        win.fill((255, 255, 255))
        btnTest1.draw(win)
        btnTest2.draw(win)
        pygame.display.update()

    if is_waiting_for_connexion :
        win.fill((255, 255, 255))
        # pick a font you have and set its size
        myfont = pygame.font.SysFont("Comic Sans MS", 30)
        # apply it to text on a label
        label = myfont.render("Python and Pygame are Fun!", 1, yellow)
        # put the label object on the screen at point x=100, y=100
        win.blit(label, (100, 100))
        pygame.display.update()


btnTest1 = button(200, 200, 100, 100, "btnTest1")
btnTest2 = button(400, 200, 100, 100, "btnTest2")

def launch_server(threads, is_waiting_for_connexion):
    if not is_waiting_for_connexion :
        is_waiting_for_connexion = True
        print(is_waiting_for_connexion)
        serv = server.Server()
        serv.create_server(host, port)
        wait = threading.Thread(target=serv.wait_for_a_connection)
        threads.append(wait)
        wait.start()
        is_waiting_for_connexion = True
    else :
        stop = threading.Thread(target=serv.socket.shutdown)
        print("shutdown")
        stop.start()

def main():
    is_waiting_for_connexion = False
    threads = [threading.Thread]
    run = True
    serv = None
    mouse = "" #l'objet que pointe la souris
    clic = False #Limiter à un clic

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                print("yes") #??????????????????????????????
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
                launch_server(threads, is_waiting_for_connexion)

            if mouse == btnTest2.id and not(clic):
                clic = True
                print("Bouton client")
                cli = client.create_client(host, port)
                client.send_obj(cli, d)
        else :
            clic = False
            
        redrawWindow()

main()
pygame.quit()
quit()