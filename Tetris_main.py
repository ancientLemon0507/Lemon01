import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from threading import Thread
from copy import deepcopy
from random import randint
import pathlib
from Tetris import Tetris_param as param

class Game:
    def __init__(self):
        self.width = param.all_row*param.cell_size
        self.height = param.all_col*param.cell_size
        self.next_width = param.next_all_row * param.next_cell_size
        self.next_height = param.next_all_col * param.next_cell_size
        self.base_path = str(pathlib.Path(__file__).parent.resolve())
        # 判断是否暂停
        self.pause = False
        # 是否加速
        self.is_speeding = False
        # 当前游戏速度
        self.now_fps = param.game_fps[0]
        # 存储最新方块的最下面位置
        self.max_position = 0
        # 存储最新方块的最上面位置(只在更新列表时更新)
        self.min_position = param.all_col
        # 开启全是方块模式
        self.square = False
        # 是否remake
        self.remake = ''
        # 保存标签
        self.position_label = None
        self.score_label = None
        self.bottom_label = None
        # 当前成绩
        self.score = 0
        # 方块属性
        self.now_tetris = {}
        self.next_tetris = {}
        # 存储已放置方块的列表
        self.exist_block_list = []
        self.root = tk.Tk()
        self.get_image()
        self.init_component()
        self.new_game()

    def get_image(self):
        try:
            self.img = Image.open(self.base_path + r'\preview.jpg').resize((750, 750))
            self.imgtk = ImageTk.PhotoImage(self.img)
        except OSError:
            pass

    # 初始化界面组件
    def init_component(self):
        self.root.title('Tetris')
        self.root.attributes('-alpha', 0.95)
        self.root.resizable(False, False)
        self.root.geometry('600x614')
        self.canva0 = tk.Canvas(self.root,  width=self.width*2, height=self.height)
        self.canva1 = tk.Canvas(self.canva0, width=self.width, height=self.height)
        self.canva2 = tk.Canvas(self.canva0, width=self.next_width, height=self.next_height)
        self.canva3 = tk.Canvas(self.canva0, width=200, height=300)
        self.scale0 = tk.Scale(self.canva0, from_=2, to=10, orient=tk.HORIZONTAL, font=('微软雅黑', 12, 'bold'))
        self.button0 = tk.Button(self.canva0, text='重来一局', font=('微软雅黑', 10, 'bold'),
                                 command=lambda: my_thread(self.retry_message))
        self.button1 = tk.Button(self.canva0, text='全变方块', font=('微软雅黑', 10, 'bold'), command=self.game_debug)
        # 以点(self.width, self.height//2)为中心绘图
        try:
            self.canva0.create_image(self.width, self.height // 2, image=self.imgtk)
            self.canva3.create_image(self.width-384, self.height-880 // 2, image=self.imgtk)
        except AttributeError:
            pass
        self.canva0.pack()
        self.canva1.grid(row=0, column=0, rowspan=4, padx=5, pady=5)
        self.canva2.grid(row=0, column=1, columnspan=2, padx=10)
        self.canva3.grid(row=1, column=1, columnspan=2, padx=10)
        self.scale0.grid(row=2, column=1, columnspan=2)
        self.button0.grid(row=3, column=1, padx=5)
        self.button1.grid(row=3, column=2)
        self.canva1.bind('<KeyPress-Left>', self.go_left)
        self.canva1.bind('<KeyPress-Right>', self.go_right)
        self.canva1.bind('<KeyPress-Up>', self.rotate_tetris)
        self.canva1.bind('<KeyPress-space>', self.game_pause)
        self.canva1.bind('<KeyPress-Down>', self.game_speeding)
        self.canva1.bind('<KeyRelease-Down>', self.stop_speeding)
        self.init_canva3_text()

    def init_canva3_text(self):
        self.canva3.create_text(50, 25, text='score:', font=('微软雅黑', 14, 'bold'), fill='#ffa500')
        self.canva3.create_text(50, 65, text='position:', font=('微软雅黑', 12, 'bold'), fill='#191970')
        self.canva3.create_text(50, 105, text='bottom:', font=('微软雅黑', 12, 'bold'), fill='#191970')
        self.canva3.create_text(60, 240, text='滑块控制帧数\n左右控制方向\n上键旋转\n下键加速\n空格暂停',
                                font=('微软雅黑', 10, 'bold'))

    def draw_canva3_text(self):
        self.canva3.delete(self.position_label)
        self.canva3.delete(self.score_label)
        self.canva3.delete(self.bottom_label)
        self.position_label = self.canva3.create_text(120, 65, text=str(self.now_tetris['position'][1])+'   '
                                                +str(self.now_tetris['position'][0]), font=('微软雅黑', 12, 'bold')
                                                      , fill='#191970')
        self.score_label = self.canva3.create_text(120, 25, text=self.score, fill='#ffa500', font=('微软雅黑', 13, 'bold'))
        self.bottom_label = self.canva3.create_text(120, 105, text=self.max_position, font=('微软雅黑', 12, 'bold')
                                                    , fill='#191970')

    # 开始新游戏
    def new_game(self):
        self.score = 0
        # 优化重开体验
        self.canva1.delete(tk.ALL)
        try:
            self.canva1.create_image(self.width, self.height // 2, image=self.imgtk)
        except AttributeError:
            pass
        self.init_background()
        self.draw_next_background()
        self.now_tetris = param.begin_tetris
        self.exist_block_list = [[7 for j in range(param.all_row+2)]for i in range(param.all_col+1)]
        self.generate_new_tetris()
        for i in range(1, param.all_row+1):
            self.exist_block_list[param.all_col][i] = 0
        for j in range(param.all_col+1):
            self.exist_block_list[j][0] = 0
            self.exist_block_list[j][param.all_row+1] = 0

    # 绘制canva2方块
    def draw_next_cell(self, row, col, color=param.shapes_color[7]):
        x0 = row * param.next_cell_size + 2
        y0 = col * param.next_cell_size + 2
        x1 = param.next_cell_size * (row + 1)
        y1 = param.next_cell_size * (col + 1)
        self.canva2.create_rectangle(x0, y0, x1, y1, fill=color, outline=color, width=1)

    # 绘制canva2方块
    def draw_next_background(self):
        for row in range(param.next_all_row):
            for col in range(param.next_all_col):
                self.draw_next_cell(row, col, param.shapes_color[7])

    # 绘制canva2方块
    def draw_next_tetris_cell(self, color=param.shapes_color[7]):
        for each in self.next_tetris['shape']:
            x0 = param.next_tetris_position[0] + each[0]
            y0 = param.next_tetris_position[1] + each[1]
            self.draw_next_cell(x0, y0, color=color)

    # 绘制方格(0，0)开始
    def draw_cell(self, row, col, color=param.shapes_color[7]):
        x0 = row * param.cell_size + 5
        y0 = col * param.cell_size + 5
        x1 = param.cell_size * (row + 1)
        y1 = param.cell_size * (col + 1)
        self.canva1.create_rectangle(x0, y0, x1, y1, fill=color, outline=color, width=1)

    def init_background(self):
        for row in range(param.all_row):
            for col in range(param.all_col):
                self.draw_cell(row, col, param.shapes_color[7])

    def draw_background(self):
        for row in range(param.all_row):
            for col in range(param.all_col):
                self.draw_cell(row, col, param.shapes_color[self.exist_block_list[col][row+1]])

    def draw_tetris_cell(self, color=param.shapes_color[7]):
        for each in self.now_tetris['shape']:
            x0 = self.now_tetris['position'][0] + each[0]
            y0 = self.now_tetris['position'][1] + each[1]
            if y0 > -1:
                self.draw_cell(x0, y0, color=color)

    # 更新方块的移动(以列表为准)
    def update_tetris_move(self):
        # 判断方块是否触碰边界或其他方块
        x_num, y_num, now_max_position, is_top = 0, 0, 0, False
        for each in self.now_tetris['shape']:
            position = [x + y for x, y in zip(self.now_tetris['position'], each)]
            # 列表下标为负时表示倒数第几行会导致游戏卡住
            if position[1] > -1:
                if self.now_tetris['speed'][0] != 0 and \
                        self.exist_block_list[position[1]][position[0]+self.now_tetris['speed'][0]+1] == 7:
                    x_num += 1
                if self.exist_block_list[position[1]+1][position[0]+1] == 7:
                    y_num += 1
                    if position[1] > now_max_position:
                        # 防止下落不成功导致position错误
                        now_max_position = position[1]
            else:
                is_top = True
                break
        if y_num == 4 or is_top:
            self.now_tetris['position'][1] += 1
            self.max_position = now_max_position+1
            if is_top:
                self.check_top_position()
        else:
            self.now_tetris['speed'][1] = 0
        if x_num == 4:
            self.now_tetris['position'][0] += self.now_tetris['speed'][0]
            if not is_top:
                self.check_vertical_move()
            self.now_tetris['speed'][0] = 0

    # 检测方块在顶部时是否会卡进其他方块以及判定结束
    def check_top_position(self):
        is_over = False
        for each in self.now_tetris['shape']:
            position = [x + y for x, y in zip(self.now_tetris['position'], each)]
            if position[1] > -1 and self.exist_block_list[position[1]][position[0]+1] != 7:
                is_over = True
                self.now_tetris['position'][1] -= 1
                self.max_position -= 1
        if is_over:
            self.game_over()

    # 检测并解决当按下左右键时方块卡进其他方块中或方块浮在半空的情况
    def check_vertical_move(self):
        y_num = 0
        for each in self.now_tetris['shape']:
            position = [x + y for x, y in zip(self.now_tetris['position'], each)]
            # 按下左右键时方块是否卡进其他方块中
            if self.exist_block_list[position[1]][position[0]+1] != 7:
                self.now_tetris['position'][0] -= self.now_tetris['speed'][0]
                return
            # 方块是否浮在半空
            if self.exist_block_list[position[1]+1][position[0]+1] == 7:
                y_num += 1
        if y_num == 4:
            self.now_tetris['speed'][1] = 1

    # 旋转方块(向左旋转90度)
    def rotate_tetris(self, event):
        # 已经碰到物体或边界时不能旋转
        if self.now_tetris['speed'][1] != 0:
            new_shape, now_max_position = [], 0
            for each in self.now_tetris['shape']:
                now_block = (each[1], -each[0])
                x0 = now_block[0] + self.now_tetris['position'][0] + self.now_tetris['speed'][0] + 1
                y0 = now_block[1] + self.now_tetris['position'][1] + 1
                if y0 > now_max_position:
                    # 防止变换不成功导致position错误
                    now_max_position = y0
                if self.exist_block_list[y0][x0] == 7 and 0 < x0 < param.all_row+1:
                    new_shape.append(now_block)
                else:
                    return
            self.max_position = now_max_position+1
            self.draw_tetris_cell()
            self.now_tetris['transform'] += 1
            self.now_tetris['transform'] %= 4
            self.now_tetris['shape'] = new_shape
            self.draw_tetris_cell(color=param.shapes_color[self.now_tetris['color']])

    # 更新方块存在列表
    def update_exist_list(self):
        for each in self.now_tetris['shape']:
            x = each[0] + self.now_tetris['position'][0]
            y = each[1] + self.now_tetris['position'][1]
            self.exist_block_list[y][x+1] = self.now_tetris['color']
            if y < self.min_position:
                self.min_position = y

    # 消除符合条件的行
    def eliminate_row(self):
        col_num = 0
        col = self.max_position
        while col > self.min_position-1:
            row_num = 0
            for row in range(1, param.all_row + 1):
                if self.exist_block_list[col][row] != 7:
                    row_num += 1
            if row_num == param.all_row:
                col_num += 1
                for each in range(col, -1, -1):
                    if each > 0:
                        self.exist_block_list[each] = self.exist_block_list[each-1]
                        self.exist_block_list[each-1] = [7 for i in range(param.all_row + 2)]
                        self.exist_block_list[each-1][0] = 0
                        self.exist_block_list[each-1][param.all_row + 1] = 0
                    else:
                        self.exist_block_list[0] = [7 for i in range(param.all_row + 2)]
                        self.exist_block_list[0][0] = 0
                        self.exist_block_list[0][param.all_row + 1] = 0
            else:
                col -= 1
        self.score += param.scores[col_num]
        self.min_position = param.all_col
        self.max_position = 0

    # 生成新的方块(修改now_tetris的值)
    def generate_new_tetris(self):
        if not self.square:
            rand = randint(0, 6)
            self.next_tetris['number'] = rand
            self.next_tetris['shape'] = param.shapes[rand]
            self.next_tetris['color'] = randint(0, 6)
            self.next_tetris['position'] = [5, -1]
            self.next_tetris['transform'] = 0
            self.next_tetris['speed'] = [0, 1]
        else:
            self.next_tetris['number'] = 0
            self.next_tetris['shape'] = param.shapes[0]
            self.next_tetris['color'] = 0
            self.next_tetris['position'] = [5, -1]
            self.next_tetris['transform'] = 0
            self.next_tetris['speed'] = [0, 1]

    def game_over(self):
        self.pause = True
        self.draw_tetris_cell(color=param.shapes_color[self.now_tetris['color']])
        tk.messagebox.showinfo('提示', '游戏结束!\n成绩为: %d' % self.score)
        self.retry_message()

    # 整合游戏运行方法
    def game_logic(self):
        self.draw_tetris_cell()
        self.change_fps()
        if not self.pause:
            if self.now_tetris['speed'][1] != 0:
                self.update_tetris_move()
                self.draw_canva3_text()
                self.draw_tetris_cell(color=param.shapes_color[self.now_tetris['color']])
            else:
                self.update_exist_list()
                self.eliminate_row()
                self.draw_background()
                self.draw_next_tetris_cell()
                # 字典直接赋值是引用,必须深拷贝
                self.now_tetris = deepcopy(self.next_tetris)
                self.generate_new_tetris()
                self.draw_next_tetris_cell(color=param.shapes_color[self.next_tetris['color']])
        else:
            self.draw_tetris_cell(color=param.shapes_color[self.now_tetris['color']])

    def go_left(self, event):
        if not self.pause:
            self.now_tetris['speed'][0] = -1

    def go_right(self, event):
        if not self.pause:
            self.now_tetris['speed'][0] = 1

    def game_pause(self, event):
        if not self.pause:
            self.pause = True
        else:
            self.pause = False

    def game_speeding(self, event):
        if not self.pause:
            self.is_speeding = True
            self.now_fps = param.game_fps[1]

    def stop_speeding(self, event):
        if not self.pause:
            self.is_speeding = False
            self.now_fps = param.game_fps[0]

    def game_debug(self):
        if not self.square:
            self.square = True
        else:
            self.square = False

    def change_fps(self):
        if not self.is_speeding and self.now_fps != 1000//self.scale0.get():
            param.game_fps[0] = 1000//self.scale0.get()
            param.game_fps[1] = param.game_fps[0]//3
            self.now_fps = param.game_fps[0]

    def retry_message(self):
        self.pause = True
        self.remake = tk.messagebox.askquestion(title='remake', message='确定重开?')
        if self.remake == 'yes':
            self.new_game()
        self.pause = False

    # 刷新游戏界面
    def game_loop(self):
        self.game_logic()
        self.root.after(self.now_fps, self.game_loop)

    def run(self):
        self.canva1.focus_set()
        my_thread(self.game_loop)
        self.root.mainloop()

# 采用线程刷新减少卡顿
def my_thread(func, *args):
    thread = Thread(target=func, args=args)
    # 守护线程
    thread.setDaemon(True)
    thread.start()

if __name__ == '__main__':
    Game().run()
