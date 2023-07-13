from PIL import Image
import numpy

# Encode = UTF-8
# 并查集迷宫

# 迷宫参数及准备图片
input_str = input("Maze size: ")
if not input_str.isnumeric():
    print("Invalid value, use default value 99.")
    MAZE_SIZE = 99
else:
    MAZE_SIZE = int(input_str)
BLOCK_SIZE = 8
MAZE_IMAGE_SIZE = (MAZE_SIZE + 2) * (BLOCK_SIZE + 1) + 1
print("Image size will be %dx%d" % (MAZE_IMAGE_SIZE, MAZE_IMAGE_SIZE))
img = Image.new("RGB", (MAZE_IMAGE_SIZE, MAZE_IMAGE_SIZE), 0xEEEEEE)

################################################################################

# 通路标记, 每格标记向左或向上是否通
NONE = 0
UP = 1
LEFT = 2
UP_LEFT = 3

# 迷宫通路标记图, 左上角为入口，右下角为出口
maze_shape = numpy.zeros(shape=(MAZE_SIZE, MAZE_SIZE), dtype=numpy.int8)
maze_shape[0][0] = UP

# 矩形并查集mask, 这是为了优化生成速度用的
maze_mask = numpy.empty(shape=(MAZE_SIZE * MAZE_SIZE, 4), dtype=int)
for i in range(MAZE_SIZE):
    for j in range(MAZE_SIZE):
        # [LEFT, RIGHT, TOP, DOWN]
        maze_mask[i * MAZE_SIZE + j] = [i, i, j, j]

# 迷宫并查集表, 记录每个坐标属于哪一个集合
maze = numpy.empty(shape=(MAZE_SIZE, MAZE_SIZE), dtype=int)
for i in range(MAZE_SIZE):
    for j in range(MAZE_SIZE):
        maze[i][j] = i * MAZE_SIZE + j


def Fill(x, y, val):

    # Fill的效果为找指定坐标(x, y)所在的集合, 然后将这个集合并入指定集合val
    # 类似于MSPaint的填色桶

    old_val = maze[x][y]
    
    # 实现以上功能有两种基本方式: 递归扩散, 或者全图扫描
    # 但是第一种容易栈溢出, 第二种在初始阶段集合较小时非常浪费时间, 所以程序中Fill的扫描范围设计成一个矩形mask
    # 每个集合都有一个矩形mask, 对应这个集合在迷宫图中占据的范围, mask外保证没有该集合的元素
    # 初始集合=格子, 因此矩形mask的大小就是一格。当两个集合合并, 就会重新计算mask使其扩大为两个集合的范围

    for x in range(maze_mask[old_val][0], maze_mask[old_val][1]+1):
        for y in range(maze_mask[old_val][2], maze_mask[old_val][3]+1):
            # 在mask范围内进行填充
            if maze[x][y] == old_val:
                maze[x][y] = val
    # 更新mask
    maze_mask[val][0] = min(maze_mask[val][0], maze_mask[old_val][0])
    maze_mask[val][1] = max(maze_mask[val][1], maze_mask[old_val][1])
    maze_mask[val][2] = min(maze_mask[val][2], maze_mask[old_val][2])
    maze_mask[val][3] = max(maze_mask[val][3], maze_mask[old_val][3])


def MakePath(x, y, drt):

    # 将指定坐标(x, y)根据方向drt尝试打通
    # 0: Up, 1: Right, 2: Down, 3:Left
    # 如果成功打通, 返回True，否则返回False

    # 打通: 将对应方向上的两个格子所在集合合并为一个集合

    if drt == 0:
        if y <= 0:
            return False
        if maze[x][y] == maze[x][y-1]:
            return False
        new_val = min(maze[x][y], maze[x][y-1])
        maze_shape[x][y] |= UP
        if maze[x][y] != new_val:
            Fill(x, y, new_val)
        elif maze[x][y-1] != new_val:
            Fill(x, y-1, new_val)
        return True
    
    elif drt == 1:
        if x >= MAZE_SIZE - 1:
            return False
        if maze[x][y] == maze[x+1][y]:
            return False
        new_val = min(maze[x][y], maze[x+1][y])
        maze_shape[x+1][y] |= LEFT
        if maze[x][y] != new_val:
            Fill(x, y, new_val)
        elif maze[x+1][y] != new_val:
            Fill(x+1, y, new_val)
        return True
    
    elif drt == 2:
        if y >= MAZE_SIZE - 1:
            return False
        if maze[x][y] == maze[x][y+1]:
            return False
        new_val = min(maze[x][y], maze[x][y+1])
        maze_shape[x][y+1] |= UP
        if maze[x][y] != new_val:
            Fill(x, y, new_val)
        elif maze[x][y+1] != new_val:
            Fill(x, y+1, new_val)
        return True
    
    elif drt == 3:
        if x <= 0:
            return False
        if maze[x][y] == maze[x-1][y]:
            return False
        new_val = min(maze[x][y], maze[x-1][y])
        maze_shape[x][y] |= LEFT
        if maze[x][y] != new_val:
            Fill(x, y, new_val)
        elif maze[x-1][y] != new_val:
            Fill(x-1, y, new_val)
        return True
    
    return False

################################################################################

# 生成迷宫
import random
import math
import time

start_time = time.time()
patching = False
# 整个迷宫被打通的标志是所有格子都属于0号集合
while numpy.any(maze):

    # 使用shuffle来实现对迷宫每一个格子都做一次打通
    rlist = numpy.arange(MAZE_SIZE * MAZE_SIZE)
    random.shuffle(rlist)
    last_print = time.time()

    for i in range(MAZE_SIZE * MAZE_SIZE):
        x = math.floor(rlist[i] / MAZE_SIZE)
        y = rlist[i] % MAZE_SIZE
        # 打通
        direction = [0, 1, 2, 3]
        random.shuffle(direction)
        for j in range(4):
            if MakePath(x, y, direction[j]):
                break
        # 显示进度
        if time.time() - last_print > 1.:
            if patching:
                print("Patching ... (%d/%d)" % (i, MAZE_SIZE * MAZE_SIZE))
            else:
                print("Generating ... (%d/%d)" % (i, MAZE_SIZE * MAZE_SIZE))
            last_print = time.time()
            # 跑路装置, 如果迷宫已经生成完毕了直接走
            if not numpy.any(maze):
                break
    
    # 由于随机访问格子的关系, 可能有那么一些格子在第一轮没有被打通
    # 没关系, 这时候再跑一轮
    patching = True

print("Generated with %.2f secs." % (time.time() - start_time))

# 迷宫->图片
start_time = time.time()
last_print = time.time()
nimg = numpy.asarray(img).copy()
# 图片比迷宫本身大一圈, 有1格的空白
for i in range(MAZE_IMAGE_SIZE - (BLOCK_SIZE + 1) * 2):
    for j in range(MAZE_IMAGE_SIZE - (BLOCK_SIZE + 1) * 2):

        x = math.floor(i / (BLOCK_SIZE+1))
        y = math.floor(j / (BLOCK_SIZE+1))
        if x >= MAZE_SIZE or y >= MAZE_SIZE:
            # PIL存储是翻转的
            nimg[j+BLOCK_SIZE+1][i+BLOCK_SIZE+1] = [0x11, 0x11, 0x11]
            continue

        xr = i % (BLOCK_SIZE+1)
        yr = j % (BLOCK_SIZE+1)
        # 根据迷宫设置像素
        if xr > 0:
            if yr > 0 or maze_shape[x][y] & UP > 0:
                continue
        else:
            if yr > 0 and maze_shape[x][y] & LEFT > 0:
                continue
            
        # PIL存储是翻转的
        nimg[j+BLOCK_SIZE+1][i+BLOCK_SIZE+1] = [0x11, 0x11, 0x11]

    # 进度条
    if time.time() - last_print > 1.:
        print("Converting ... (%d/%d)" % (i * (MAZE_IMAGE_SIZE - (BLOCK_SIZE + 1) * 2) + j, \
            (MAZE_IMAGE_SIZE - (BLOCK_SIZE + 1) * 2) * (MAZE_IMAGE_SIZE - (BLOCK_SIZE + 1) * 2)))
        last_print = time.time()
# 在右下角放置出口
for i in range(BLOCK_SIZE):
    nimg[MAZE_IMAGE_SIZE-BLOCK_SIZE-2][MAZE_IMAGE_SIZE-BLOCK_SIZE-3-i] = [0xEE, 0xEE, 0xEE]

print("Converted into image with %.2f secs." % (time.time() - start_time))

# 保存到文件
start_time = time.time()
img = Image.fromarray(nimg)
img.save("Maze/Maze.png", format="png")
print("Saved to file in %.2f secs." % (time.time() - start_time))