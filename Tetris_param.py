"""
:param all_col 方格所有行数
:param all_row 方格所有列数
:param cell_size 方格大小
"""
all_col = 20
all_row = 12
cell_size = 30
"""
:param next_all_col canva2所有行数
:param next_all_row canva2所有列数
:param next_cell_size canva2方格大小
:param next_tetris_position canva2方块原点位置
"""
next_all_col = 4
next_all_row = 5
next_cell_size = 20
next_tetris_position = (2, 2)
"""
:param shapes 各种俄罗斯方块的相对位置
:param shapes_color 各种俄罗斯方块的颜色
"""
shapes = {
    # 方块, 以右下小方块为相对原点位置
    0: [(-1, -1), (0, -1), (0, 0), (-1, 0)],
    # Z字形
    1: [(-1, -1), (0, -1), (0, 0), (1, 0)],
    # S字形
    2: [(-1, 0), (0, 0), (0, -1), (1, -1)],
    # T字形
    3: [(-1, -1), (0, -1), (1, -1), (0, 0)],
    # I字形
    4: [(0, -2), (0, -1), (0, 0), (0, 1)],
    # L字形
    5: [(-1, -2), (-1, -1), (-1, 0), (0, 0)],
    # J字形
    6: [(-1, 0), (0, 0), (0, -1), (0, -2)]
}
shapes_color = (
    # 方块颜色
    '#b22222',
    '#008b8b',
    '#006400',
    '#ff8c00',
    '#9932cc',
    '#4682b4',
    '#e9967a',
    # 默认背景颜色
    '#F0F8FF'
)
"""
:param game_fps 游戏可变换的帧数
:param begin_tetris 初始方块数据 
:param scores 消除分数表
"""
game_fps = [500, 500//3]
begin_tetris = {
    # 编号
    'number': 0,
    # 形状
    'shape': shapes[0],
    # 颜色
    'color': 7,
    # 原点位置
    'position': [5, all_col-1],
    # 变换次数
    'transform': 0,
    # 速度方向
    'speed': [0, 0]
}
scores = (
    0,
    # 消一行
    1,
    # 消两行
    3,
    # 消三行
    10,
    # 消四行
    30
)
