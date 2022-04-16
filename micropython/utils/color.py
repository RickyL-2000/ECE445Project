# 字体色
# print("\033[30m%s\033[0m"%"黑色")
# print("\033[31m%s\033[0m"%"红色")
# print("\033[32m%s\033[0m"%"绿色")
# print("\033[33m%s\033[0m"%"黄色")
# print("\033[34m%s\033[0m"%"蓝色")
# print("\033[35m%s\033[0m"%"紫红色")
# print("\033[36m%s\033[0m"%"青蓝色")
# print("\033[37m%s\033[0m"%"白色")

# 背景色
# print("\033[0;37;40m%s\033[0m"%"黑底")
# print("\033[0;37;41m%s\033[0m"%"红底")
# print("\033[0;37;42m%s\033[0m"%"绿底")
# print("\033[0;37;43m%s\033[0m"%"黄底")
# print("\033[0;37;44m%s\033[0m"%"蓝底")
# print("\033[0;37;45m%s\033[0m"%"紫红底")
# print("\033[0;37;46m%s\033[0m"%"青蓝底")
# print("\033[0;30;47m%s\033[0m"%"白底黑字")

# 纯字体色
# print("\033[90m%s\033[0m"%"黑色")
# print("\033[91m%s\033[0m"%"红色")
# print("\033[92m%s\033[0m"%"绿色")
# print("\033[93m%s\033[0m"%"黄色")
# print("\033[94m%s\033[0m"%"蓝色")
# print("\033[95m%s\033[0m"%"紫红色")
# print("\033[96m%s\033[0m"%"青蓝色")
# print("\033[97m%s\033[0m"%"白色")

def red(s):
    return "\033[91m%s\033[0m" % s
def r(s):
    return "\033[91m%s\033[0m" % s

def green(s):
    return "\033[92m%s\033[0m" % s
def g(s):
    return "\033[92m%s\033[0m" % s

def yellow(s):
    return "\033[93m%s\033[0m" % s
def y(s):
    return "\033[93m%s\033[0m" % s

def blue(s):
    return "\033[94m%s\033[0m" % s
def b(s):
    return "\033[94m%s\033[0m" % s




def test_color():
    s = "test_color"
    print(r(s))
    print(g(s))
    print(b(s))
    print(y(s))
    print("\033[95m%s\033[0m" % s)
    print("\033[96m%s\033[0m" % s)
    print("\033[97m%s\033[0m" % s)
    print("\033[98m%s\033[0m" % s)
    print("\033[99m%s\033[0m" % s)
    return
