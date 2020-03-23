import pygame

pygame.init()

win = pygame.display.set_mode((500, 500))

pygame.display.set_caption("First Game")
clock = pygame.time.Clock()

class button(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hitbox = (self.x, self.y, self.width, self.height)
    def draw(self, win):
        pygame.draw.rect(win, (0,0,0), self.hitbox)

def redrawWindow():
    win.fill((255, 255, 255))
    boutonTest.draw(win)
    pygame.display.update()

def main():
    run = True

    boutonTest = button(200, 200, 100, 100)

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        redrawWindow()

main()
pygame.quit()
quit()