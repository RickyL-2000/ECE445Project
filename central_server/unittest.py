from control import CircularQueue

cq = CircularQueue(5)
for i in range(10):
    cq.put(i, block=False)
    print(cq.queue)


import pygame
pygame.mixer.init()

track = pygame.mixer.music.load(r"D:\User\Dashujv\语音分析\data\声声慢.mp3")
pygame.mixer.music.play()

pygame.mixer.music.pause() #暂停
pygame.mixer.music.unpause()#取消暂停