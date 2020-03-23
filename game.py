import pygame

pygame.init()

#Dimensions écran
winWidth = 500
winHeight = 500

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
    win.fill((255, 255, 255))
    btnTest.draw(win)
    pygame.display.update()

btnTest = button(200, 200, 100, 100, "btnTest")

def main():
    run = True
    mouse = "" #l'objet que pointe la souris
    clic = False #Limiter à un clic

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
    
        #Test position souris
        xMouse, yMouse = pygame.mouse.get_pos() #Position de la souris
        if xMouse > btnTest.x and xMouse < btnTest.xMax and yMouse > btnTest.y and yMouse < btnTest.yMax :
            mouse = btnTest.id
        else :
            mouse = ""

        #Clic bouton
        if pygame.mouse.get_pressed()[0]: #Si clic gauche
            if mouse == btnTest.id and not(clic):
                clic = True
                print("Bouton")
        else :
            clic = False
            
        redrawWindow()

main()
pygame.quit()
quit()