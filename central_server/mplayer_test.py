import sys
import pygame

class Control:
    def __init__(self, surface, name=None, size=(0, 0), pos=(0, 0)):
        self.screen = None
        self.surface = surface
        self.name = name
        self.size = size
        self.pos = pos

        # self.instance = pygame.image.load(img_path)
        self.surface = pygame.transform.scale(self.surface, self.size)
        self.rect = self.surface.get_rect()

    def check_hover(self, mouse_x, mouse_y):
        return self.pos[0] < mouse_x < self.rect.width + self.pos[0] \
            and self.pos[1] < mouse_y < self.rect.height+self.pos[1]

    def display(self, screen, pos=None):
        self.screen = screen
        if pos is not None:
            self.pos = pos
        self.screen.blit(self.surface, self.pos)

    def set_surface(self, surface, show=True):
        self.surface = surface
        self.surface = pygame.transform.scale(self.surface, self.size)
        # self.rect = self.surface.get_rect()
        # if show:
        #     self.display(self.screen)
        self.screen.blit(self.surface, self.pos)
        pygame.display.flip()

class Button(Control):
    def __init__(self, surface, name=None, size=(0, 0), pos=(0, 0)):
        super(Button, self).__init__(surface, name, size, pos)

if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode(pygame.Rect(0, 0, 800, 600).size)
    pygame.display.set_caption("Music Player")
    pygame.time.Clock().tick(30)    # fps <= 30

    background_img = pygame.image.load("images/20200202_150926840_iOS.jpg")
    background_img = pygame.transform.scale(background_img, (800, 600))
    screen.blit(background_img, (0, 0))

    surfaces = {
        "play_bt": pygame.image.load("images/Player, play.png"),
        "pause_bt": pygame.image.load("images/Player, pause.png")
    }

    play_bt = Button(surfaces["play_bt"], name="play_bt", size=(100, 100), pos=(250, 500))

    pygame.display.flip()

    running = True
    while running:
        # play_bt = Button(surfaces["play_bt"], name="play_bt", size=(100, 100), pos=(250, 500))
        screen.blit(background_img, (0, 0))
        play_bt.display(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if play_bt.check_hover(mouse_x, mouse_y):
                    play_bt.set_surface(surfaces["pause_bt"])
                    # screen.blit(pygame.transform.scale(surfaces["pause_bt"], play_bt.size), play_bt.pos)
                    # play_bt = Button(surfaces["pause_bt"], name="play_bt", size=(100, 100), pos=(250, 500))
                print(event.button)

        pygame.display.flip()
