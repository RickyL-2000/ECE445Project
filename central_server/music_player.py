import glob

from mutagen.mp3 import MP3
import pygame


# pygame.mixer.music.load()  ——  载入一个音乐文件用于播放
# pygame.mixer.music.play()  ——  开始播放音乐流
# pygame.mixer.music.rewind()  ——  重新开始播放音乐
# pygame.mixer.music.stop()  ——  结束音乐播放
# pygame.mixer.music.pause()  ——  暂停音乐播放
# pygame.mixer.music.unpause()  ——  恢复音乐播放
# pygame.mixer.music.fadeout()  ——  淡出的效果结束音乐播放
# pygame.mixer.music.set_volume()  ——  设置音量
# pygame.mixer.music.get_volume()  ——  获取音量
# pygame.mixer.music.get_busy()  ——  检查是否正在播放音乐
# pygame.mixer.music.set_pos()  ——  设置播放的位置
# pygame.mixer.music.get_pos()  ——  获取播放的位置
# pygame.mixer.music.queue()  ——  将一个音乐文件放入队列中，并排在当前播放的音乐之后
# pygame.mixer.music.set_endevent()  ——  当播放结束时发出一个事件
# pygame.mixer.music.get_endevent()  ——  获取播放结束时发送的事件

class MusicPlayer:
    def __init__(self, music_dir):
        pygame.mixer.init()
        self.music_files = glob.glob(f'{music_dir}/*.mp3')
        self.cur_music_idx = 0
        self.cur_music_pos = 0.0
        pygame.mixer.music.load(self.music_files[self.cur_music_idx])
        for i in self.music_files:
            pygame.mixer.music.queue(i)

        self._update_music_info()

        self.volume = 0.8
        self.status = "stop"    # stop, play, pause

        self.surfaces = {
            "background": pygame.image.load("images/20200202_150926840_iOS.jpg"),
            "play_bt": pygame.image.load("images/Player, play.png"),
            "next_bt": pygame.image.load("images/Player, next.png"),
            "prev_bt": pygame.image.load("images/Player, prev.png"),
            "pause_bt": pygame.image.load("images/Player, pause.png"),
            "stop_bt": pygame.image.load("images/Player, stop.png"),
            "play_bt_fill": pygame.image.load("images/Player, play (fill).png"),
            "next_bt_fill": pygame.image.load("images/Player, next (fill).png"),
            "prev_bt_fill": pygame.image.load("images/Player, prev (fill).png"),
            "pause_bt_fill": pygame.image.load("images/Player, pause (fill).png"),
            "stop_bt_fill": pygame.image.load("images/Player, stop (fill).png"),
            "record": pygame.image.load("images/Player, rec, record.png"),
            "circle": pygame.image.load("images/circle.png"),
        }

        self.components = {
            "root_window": pygame.Rect(0, 0, 800, 600),
            "play_bt": Button(self.surfaces["play_bt"], name="play_bt", size=(80, 80), pos=(430, 420)),
            "next_bt": Button(self.surfaces["next_bt"], name="next_bt", size=(80, 80), pos=(570, 420)),
            "stop_bt": Button(self.surfaces["stop_bt"], name="stop_bt", size=(80, 80), pos=(290, 420)),
            "prev_bt": Button(self.surfaces["prev_bt"], name="prev_bt", size=(80, 80), pos=(150, 420)),
            "p_bar": ProgressBar(self.surfaces["circle"], name="p_bar", size=(30, 30), pos=(100, 420), length=600,
                                 src=(100, 400), dst=(700, 400), height=2, line_color=(0, 100, 100))
        }

        self.screen = None

        self.running = False

    def play(self, idx=-1, start=0.0):
        pygame.mixer.music.stop()
        if idx >= 0:
            self.cur_music_idx = idx
        pygame.mixer.music.load(self.music_files[self.cur_music_idx])
        self._update_music_info()
        pygame.mixer.music.play(start=start)

    def pause(self):
        self.status = "pause"
        pygame.mixer.music.pause()

    def unpause(self):
        self.status = "play"
        pygame.mixer.music.unpause()

    def stop(self):
        self.status = "stop"
        self.cur_music_pos = 0.0
        pygame.mixer.music.stop()

    def get_busy(self):
        if pygame.mixer.music.get_busy():
            self.status = "play"
            return True
        return False

    def rewind(self):
        self.status = "play"
        pygame.mixer.music.play(self.cur_music_idx)

    def next_music(self):
        self.cur_music_idx = (self.cur_music_idx + 1) % len(self.music_files)
        self.play()

    def prev_music(self):
        self.cur_music_idx = (self.cur_music_idx - 1) % len(self.music_files)
        self.play()

    def set_volume(self, vol):
        self.volume = vol
        pygame.mixer.music.set_volume(self.volume)

    def _update_music_info(self):
        self.cur_music_info = {
            "length": MP3(self.music_files[self.cur_music_idx]).info.length  # in sec
        }

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.components["root_window"].size)
        pygame.display.set_caption("Music Player")
        pygame.time.Clock().tick(30)    # fps <= 30

        # show window
        self.surfaces["background"] = pygame.transform.scale(self.surfaces["background"],
                                                             self.components["root_window"].size)

        self.running = True
        while self.running:

            self.screen.blit(self.surfaces["background"], (0, 0))
            self.components["play_bt"].display(self.screen)
            self.components["next_bt"].display(self.screen)
            self.components["prev_bt"].display(self.screen)
            self.components["stop_bt"].display(self.screen)

            self.cur_music_pos = pygame.mixer.music.get_pos() / 1000
            # print(self.cur_music_pos)
            self.components["p_bar"].update(self.screen, self.cur_music_pos / self.cur_music_info["length"])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        print("K_RIGHT")
                        self.next_music()
                    if event.key == pygame.K_LEFT:
                        print("K_LEFT")
                        self.prev_music()
                    if event.key == pygame.K_SPACE:
                        print("K_SPACE")
                        if self.status == "pause":
                            self.unpause()
                        elif self.get_busy():
                            self.pause()
                        else:
                            self.play(self.cur_music_idx)
                    if event.key == pygame.K_UP:
                        print("K_UP")
                        self.volume += 0.1
                        self.set_volume(self.volume)
                    if event.key == pygame.K_DOWN:
                        print("K_DOWN")
                        self.volume -= 0.1
                        self.set_volume(self.volume)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if self.components["play_bt"].check_hover(mouse_x, mouse_y):
                        if self.status == "play":
                            self.components["play_bt"].set_surface(self.surfaces["play_bt"])
                            self.pause()
                        elif self.status == "pause":
                            self.components["play_bt"].set_surface(self.surfaces["pause_bt"])
                            self.unpause()
                        elif self.status == "stop":
                            self.components["play_bt"].set_surface(self.surfaces["pause_bt"])
                            self.rewind()
                    elif self.components["next_bt"].check_hover(mouse_x, mouse_y):
                        self.next_music()
                    elif self.components["prev_bt"].check_hover(mouse_x, mouse_y):
                        self.prev_music()
                    elif self.components["stop_bt"].check_hover(mouse_x, mouse_y):
                        self.components["play_bt"].set_surface(self.surfaces["play_bt"])
                        self.stop()

            pygame.display.update()

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
        if show:
            self.display(self.screen)


class Button(Control):
    def __init__(self, surface, name=None, size=(0, 0), pos=(0, 0)):
        super(Button, self).__init__(surface, name, size, pos)


class ProgressBar(Control):
    # only support horizontal progress bar
    def __init__(self, surface, name=None, size=(0, 0), pos=(0, 0), length=600, src=(100, 400), dst=(700, 400), height=2, line_color=(0, 100, 100)):
        super(ProgressBar, self).__init__(surface, name, size, pos)
        self.length = length
        self.height = height
        self.progress = 0.0     # [0.0, 1.0]
        self.line_color = line_color
        self.src = src
        self.dst = dst

    def update(self, screen, progress):
        self.progress = progress
        x = self.src[0] + self.length * progress - self.size[0]//2
        self.display(screen, pos=(x, self.src[1]+self.height//2-self.size[1]//2))

    def display(self, screen, pos=None):
        self.screen = screen
        if pos is not None:
            self.pos = pos
        pygame.draw.line(screen, self.line_color, self.src, self.dst, self.height)
        self.screen.blit(self.surface, self.pos)

if __name__ == "__main__":
    music_player = MusicPlayer(r"D:\ECE445Project\central_server\music")
    music_player.run()
