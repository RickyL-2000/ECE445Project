import glob
import os
import time

from mutagen.mp3 import MP3
import pygame

from music_analyzer import MusicAnalyzer


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
    def __init__(self, music_dir, music_analyzer):
        pygame.mixer.init()
        self.music_dir = music_dir
        self.music_analyzer = music_analyzer
        self.music_files = glob.glob(f'{music_dir}/*.mp3')
        self.cur_music_idx = 0
        self.cur_music_pos = 0.0    # sec
        # pygame.mixer.music.load(self.music_files[self.cur_music_idx])
        for i in self.music_files:
            pygame.mixer.music.queue(i)
        self.play()
        self.pause()

    def play(self, start=0.0):
        pygame.mixer.music.stop()
        self.cur_music_pos = start
        pygame.mixer.music.load(self.music_files[self.cur_music_idx])
        pygame.mixer.music.play(start=start)

    def pause(self):
        pygame.mixer.music.pause()

    def unpause(self):
        pygame.mixer.music.unpause()

    def stop(self):
        self.cur_music_pos = 0.0
        pygame.mixer.music.stop()

    def get_busy(self):
        return pygame.mixer.music.get_busy()

    def get_color(self):
        """code: rgb/RGB / hsv/HSV """
        self.cur_music_pos = pygame.mixer.music.get_pos() / 1000
        return self.music_analyzer.get_color(self.cur_music_pos)

    def gen_color_seq(self):
        self.music_analyzer.gen_color_seq(f_path=self.music_files[self.cur_music_idx])


class MusicPlayerGUI:
    def __init__(self, music_dir, music_analyzer):
        pygame.mixer.init()
        self.music_dir = music_dir
        self.music_analyzer = music_analyzer
        # self.music_files = glob.glob(f'{music_dir}/*')
        self.music_files = glob.glob(f'{music_dir}/*.mp3')
        self.cur_music_idx = 0
        self.cur_music_pos = 0.0    # in sec
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
            "refresh_bt": pygame.image.load("images/refresh.png"),
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
            "next_bt": Button(self.surfaces["next_bt"], name="next_bt", size=(80, 80), pos=(570, 490)),
            "play_bt": Button(self.surfaces["play_bt"], name="play_bt", size=(80, 80), pos=(465, 490)),
            "stop_bt": Button(self.surfaces["stop_bt"], name="stop_bt", size=(80, 80), pos=(360, 490)),
            "prev_bt": Button(self.surfaces["prev_bt"], name="prev_bt", size=(80, 80), pos=(255, 490)),
            "refresh_bt": Button(self.surfaces["refresh_bt"], name="refresh_bt", size=(54, 54), pos=(155, 503)),
            "p_bar": ProgressBar(self.surfaces["circle"], name="p_bar", size=(30, 30), pos=(100, 470), length=600,
                                 src=(100, 470), dst=(700, 470), height=2, line_color=(0, 100, 100)),
            "text_lst": TextList(None, name="text_lst", size=(500, 250), pos=(130, 80), num=5, spacing=10,
                                 margin=(5, 5, 5, 5), font=None, font_size=35, color=(58, 75, 91), bg_color=None),
            "msg_box": TextBox(None, name="msg_box", size=(300, 40), pos=(135, 390), text="", font=None,
                               font_size=35, color=(76, 88, 94), bg_color=None)
        }

        self.screen = None
        self.cursor = 0

        self.running = False

    def play(self, idx=-1, start=0.0, preload=False, pregen=True):
        pygame.mixer.music.stop()
        if idx >= 0:
            self.cur_music_idx = idx
        self.cur_music_pos = start
        if pregen:
            self.gen_color_seq()
        # self.music_analyzer.gen_color_seq(self.music_files[self.cur_music_idx])
        pygame.mixer.music.load(self.music_files[self.cur_music_idx])
        self._update_music_info()
        if not preload:
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
        self.status = "stop"
        self.cur_music_idx = (self.cur_music_idx + 1) % len(self.music_files)
        self.play(preload=True, pregen=False)
        if self.cur_music_idx >= self.cursor + len(self.components["text_lst"]):
            self.cursor = self.cur_music_idx - len(self.components["text_lst"]) + 1
        if self.cur_music_idx == 0:
            self.cursor = 0

    def prev_music(self):
        self.status = "stop"
        self.cur_music_idx = (self.cur_music_idx - 1) % len(self.music_files)
        self.play(preload=True, pregen=False)
        if self.cur_music_idx < self.cursor:
            self.cursor = self.cur_music_idx
        if self.cur_music_idx == len(self.music_files) - 1:
            self.cursor = len(self.music_files) - len(self.components["text_lst"])

    def set_volume(self, vol):
        self.volume = vol
        pygame.mixer.music.set_volume(self.volume)

    def _update_music_info(self):
        self.cur_music_info = {
            "length": MP3(self.music_files[self.cur_music_idx]).info.length  # in sec
        }

    def _update_music_files(self):
        cur_music = self.music_files[self.cur_music_idx]
        self.music_files = glob.glob(f'{self.music_dir}/*.mp3')
        if len(self.music_files) > 0:
            cur_music_idx = self.music_files.index(cur_music)
            if cur_music_idx == -1:
                self.stop()
                self.cur_music_idx = 0
                self.cur_music_pos = 0.0  # in sec
                pygame.mixer.music.load(self.music_files[self.cur_music_idx])
            elif cur_music_idx >= 0:
                self.cur_music_idx = cur_music_idx
            for file in self.music_files:
                if os.path.exists(file):
                    pygame.mixer.music.queue(file)
        else:
            self.stop()
            self.cur_music_idx = 0
            self.cur_music_pos = 0.0  # in sec

    def get_color(self, code="rgb"):
        """code: rgb/RGB / hsv/HSV """
        return self.music_analyzer.get_color(self.cur_music_pos, code=code)

    def gen_color_seq(self):
        self.pop_msg("Analyzing...")
        self.music_analyzer.gen_color_seq(f_path=self.music_files[self.cur_music_idx])
        self.pop_msg("Done")
        time.sleep(0.2)
        self.pop_msg("")

    def pop_msg(self, msg):
        self.components["msg_box"].set_text(self.screen, msg)
        self.components["msg_box"].display(self.screen)
        pygame.display.update()

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.components["root_window"].size)
        pygame.display.set_caption("Music Player")
        pygame.time.Clock().tick(30)    # fps <= 30

        # show window
        self.surfaces["background"] = pygame.transform.scale(self.surfaces["background"],
                                                             self.components["root_window"].size)

        # self.gen_color_seq()

        self.running = True
        while self.running:

            for i in range(len(self.components["text_lst"])):
                if i + self.cursor < len(self.music_files):
                    self.components["text_lst"][i]\
                        .set_text(self.screen,
                                  f"{i + self.cursor:02}   " + os.path.basename(self.music_files[i + self.cursor]))
                else:
                    self.components["text_lst"][i].set_text(self.screen, "")
                if i + self.cursor == self.cur_music_idx:
                    self.components["text_lst"][i].set_color(self.screen, color=(0, 0, 0), bg_color=None)
                else:
                    self.components["text_lst"][i].set_color(self.screen, color=(58, 75, 91), bg_color=None)

            self.screen.blit(self.surfaces["background"], (0, 0))
            self.components["play_bt"].display(self.screen)
            self.components["next_bt"].display(self.screen)
            self.components["prev_bt"].display(self.screen)
            self.components["stop_bt"].display(self.screen)
            self.components["refresh_bt"].display(self.screen)
            self.components["text_lst"].display(self.screen)
            self.components["msg_box"].display(self.screen)

            if self.get_busy():
                self.components["play_bt"].set_surface(self.surfaces["pause_bt"])
            else:
                self.components["play_bt"].set_surface(self.surfaces["play_bt"])

            self.cur_music_pos = pygame.mixer.music.get_pos() / 1000
            # print(self.cur_music_pos)
            self.components["p_bar"].update(self.screen, self.cur_music_pos / self.cur_music_info["length"])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.next_music()
                    if event.key == pygame.K_LEFT:
                        self.prev_music()
                    if event.key == pygame.K_SPACE:
                        if self.status == "pause":
                            self.unpause()
                        elif self.get_busy():
                            self.pause()
                        else:
                            self.play(self.cur_music_idx)
                    if event.key == pygame.K_UP:
                        self.volume += 0.1
                        self.set_volume(self.volume)
                    if event.key == pygame.K_DOWN:
                        self.volume -= 0.1
                        self.set_volume(self.volume)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if self.components["play_bt"].check_hover(mouse_x, mouse_y) and event.button == 1:  # 1: left click
                        if self.status == "play":
                            self.pause()
                        elif self.status == "pause":
                            self.unpause()
                        elif self.status == "stop":
                            self.play()
                    elif self.components["next_bt"].check_hover(mouse_x, mouse_y) and event.button == 1:
                        self.next_music()
                    elif self.components["prev_bt"].check_hover(mouse_x, mouse_y) and event.button == 1:
                        self.prev_music()
                    elif self.components["stop_bt"].check_hover(mouse_x, mouse_y) and event.button == 1:
                        self.stop()
                    elif self.components["refresh_bt"].check_hover(mouse_x, mouse_y) and event.button == 1:
                        self._update_music_files()
                    # wheel
                    elif self.components["text_lst"].check_hover(mouse_x, mouse_y):
                        if event.button == 4:   # slid up
                            self.cursor = self.cursor - 1 if self.cursor > 0 else 0
                        elif event.button == 5:   # slid down
                            self.cursor = self.cursor + 1 \
                                if self.cursor < len(self.music_files)-1 else len(self.music_files) - 1

            pygame.display.update()


class BaseControl:
    def __init__(self, surface, name=None, size=(0, 0), pos=(0, 0)):
        self.screen = None
        self.surface = surface
        self.name = name
        self.size = size
        self.pos = pos

        # self.instance = pygame.image.load(img_path)
        if surface is not None:
            self.surface = pygame.transform.scale(self.surface, self.size)
            self.rect = self.surface.get_rect()
        else:
            self.rect = pygame.Rect((pos[0], pos[1], size[1], size[0]))

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


class Button(BaseControl):
    def __init__(self, surface, name=None, size=(0, 0), pos=(0, 0)):
        super(Button, self).__init__(surface, name, size, pos)


class ProgressBar(BaseControl):
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

class TextBox(BaseControl):
    def __init__(self, surface, name=None, size=(0, 0), pos=(0, 0), text="", font=None, font_size=20,
                 color=(0, 0, 0), bg_color=None):
        super(TextBox, self).__init__(surface, name, size, pos)
        self.text = text
        self.font = font
        self.font_size = font_size
        self.color = color
        self.bg_color = bg_color

    def set_text(self, screen, text):
        self.text = text
        self.display(screen)

    def set_color(self, screen, color, bg_color=None):
        self.color = color
        self.bg_color = bg_color
        self.display(screen)

    def display(self, screen, pos=None):
        self.screen = screen
        if pos is not None:
            self.pos = pos
        if self.font is None:
            self.font = pygame.font.Font(None, self.font_size)
        self.surface = self.font.render(self.text, True, self.color, self.bg_color)
        self.screen.blit(self.surface, self.pos)

class TextList(BaseControl):
    # only support vertical list
    def __init__(self, surface, name=None, size=(0, 0), pos=(0, 0), num=5, spacing=30, margin=(5, 5, 5, 5),
                 font=None, font_size=20, color=(0, 0, 0), bg_color=None):
        super(TextList, self).__init__(surface, name, size, pos)
        self.text_list = []
        self.num = num
        self.spacing = spacing
        self.margin = margin    # top, down, left, right
        self.font = font
        self.font_size = font_size
        self.color = color
        self.bg_color = bg_color

        for i in range(num):
            textbox_size = (size[0], (size[1]-margin[0]-margin[1]+spacing)/num)
            textbox_pos = (pos[0]+margin[2], pos[1]+margin[0]+i*(textbox_size[1]+spacing))
            textbox = TextBox(surface=None, name="textbox", size=textbox_size, pos=textbox_pos, text="",
                              font=font, font_size=font_size, color=color, bg_color=bg_color)
            self.text_list.append(textbox)

    def __getitem__(self, idx):
        return self.text_list[idx]

    def __len__(self):
        return self.num

    def display(self, screen, pos=None):
        self.screen = screen
        if pos is not None:
            self.pos = pos
        for i in range(self.num):
            self.text_list[i].display(screen)

if __name__ == "__main__":
    manalyzer = MusicAnalyzer()
    music_player = MusicPlayerGUI(r"D:\ECE445Project\central_server\music", manalyzer)
    music_player.run()
