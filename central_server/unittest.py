# from control import CircularQueue
#
# cq = CircularQueue(5)
# for i in range(10):
#     print(cq.queue)
#     cq.put(i, block=False)
#
import time

from music_player import MusicPlayer

mp = MusicPlayer(r"D:\NextcloudRoot\course\ECE445\ECE445Project\central_server\music")

mp.play()
time.sleep(10)
mp.pause()
time.sleep(5)
mp.unpause()
time.sleep(10)
