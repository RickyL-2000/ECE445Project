from control import Control
from dynamics import Dynamics
from utils.config import LIGHT_MOCK, LIGHT_PORT, LIGHT_1
from music_player import MusicPlayer

dynamics = Dynamics()
# mplayer = MusicPlayer(r"D:\NextcloudRoot\course\ECE445\ECE445Project\central_server\music")
mplayer = MusicPlayer(r"D:\ECE445Project\central_server\music")

light_config = {"lightB":
                    {"host": LIGHT_1,
                     "port": LIGHT_PORT},
                }
control = Control(dynamics, None, mplayer, light_config)

control.run()

if __name__ == "__main__":
    pass
