from control import Control
from dynamics import Dynamics
from utils.config import LIGHT_MOCK, LIGHT_PORT, LIGHT_1
from music_player import MusicPlayer
from music_analyzer import MusicAnalyzer

manalyzer = MusicAnalyzer()

dynamics = Dynamics()
mplayer = MusicPlayer(r"D:\NextcloudRoot\course\ECE445\ECE445Project\central_server\music", manalyzer)
# mplayer = MusicPlayer(r"D:\ECE445Project\central_server\music")
mplayer.gen_color_seq()

light_config = {"lightB":
                    {"host": LIGHT_1,
                     "port": LIGHT_PORT},
                }

# music analyzer 使用方法：传入音乐的文件路径
# manalyzer = MusicAnalyzer()
# manalyzer.gen_color_seq(f_path="")

control = Control(dynamics, mplayer, light_config)

control.run()