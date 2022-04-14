'''
Author: your name
Date: 2022-04-04 21:00:32
LastEditTime: 2022-04-07 10:33:46
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: \a\b.py
'''
class var:
    def __init__(self):
        self.xhat = [0]
        self.Px = [1]
        self.xhatminus = []
        self.Pxminus = []
        self.Kx = []
        self.yhat = [0]
        self.Py = [1]
        self.yhatminus = []
        self.Pyminus = []
        self.Ky = []
        self.zhat = [0]
        self.Pz = [1]
        self.zhatminus = []
        self.Pzminus = []
        self.Kz = []
v = var()