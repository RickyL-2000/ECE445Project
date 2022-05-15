from control import Control
from dynamics import Dynamics
from utils.config import LIGHT_MOCK, LIGHT_PORT, LIGHT_1
from music_player import MusicPlayer
from music_analyzer import MusicAnalyzer

if __name__ == "__main__":

    # music analyzer 使用方法：传入音乐的文件路径
    manalyzer = MusicAnalyzer()

    dynamics = Dynamics()
    # mplayer = MusicPlayer(music_dir=r"D:\NextcloudRoot\course\ECE445\ECE445Project\central_server\music")
    mplayer = MusicPlayer(music_dir=r"D:\ECE445Project\central_server\music", music_analyzer=manalyzer)

    light_config = {"lightB":
                        {"host": LIGHT_1,
                         "port": LIGHT_PORT},
                    }

    control = Control(dynamics, mplayer, light_config)

    control.run()
