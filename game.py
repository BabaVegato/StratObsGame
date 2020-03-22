import pygame

pygame.init()

win = pygame.display.set_mode((500, 500))

pygame.display.set_caption("First Game")
clock = pygame.time.Clock()

def redrawWindow():
    win.fill((255, 255, 255))
    pygame.display.update()

def main():
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        redrawWindow()

main()