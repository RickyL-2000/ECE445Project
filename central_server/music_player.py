import glob

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
        pygame.mixer.music.load(self.music_files[self.cur_music_idx])
        for i in self.music_files:
            pygame.mixer.music.queue(i)

    def play(self):
        pygame.mixer.music.play()

    def pause(self):
        pygame.mixer.music.pause()

    def unpause(self):
        pygame.mixer.music.unpause()

    def get_busy(self):
        return pygame.mixer.music.get_busy()