from control import Control
from dynamics import Dynamics
from utils.config import LIGHT_MOCK, LIGHT_PORT
from music_player import MusicPlayer

dynamics = Dynamics()
mplayer = MusicPlayer(r"D:\NextcloudRoot\course\ECE445\ECE445Project\central_server\music")

light_config = {"lightB":
                    {"host":LIGHT_MOCK,
                     "port":LIGHT_PORT},
                }
control = Control(dynamics, None, mplayer, light_config)

control.run()
