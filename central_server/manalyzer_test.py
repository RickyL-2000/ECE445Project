# %%
from music_analyzer import MusicAnalyzer

if __name__ == "__main__":
    manalyzer = MusicAnalyzer()
    f_path = "music/qilixiang.mp3"
    manalyzer.gen_color_seq(f_path)
