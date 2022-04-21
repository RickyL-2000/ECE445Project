import random

with open("temp.txt", 'w') as f:
    f.write("43.07\n")
    for i in range(100):
        f.write(f"{random.randint(0, 255)} {random.randint(0, 255)} {random.randint(0, 255)}\n")
