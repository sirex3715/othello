import tkinter as tk
import numpy as np
from tkinter import messagebox

# 定数
DIR_INDEX = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1)]
MOVABLE_DIR_BIT = [0b00000001, 0b00000010, 0b00000100, 0b00001000,
                   0b00010000, 0b00100000, 0b01000000, 0b10000000]
REVERSIBLE_DIR_BIT = [0b11111110, 0b11111101, 0b11111011, 0b11110111,
                      0b11101111, 0b11011111, 0b10111111, 0b01111111]
BOARD_SIZE = 8
BLACK = 1
WHITE = -1
WALL = 2
X_TAG = ["a", "b", "c", "d", "e", "f", "g", "h"]
Y_TAG = ["1", "2", "3", "4", "5", "6", "7", "8"]


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("othello")
        self.canvas = tk.Canvas(self, bg="black", height=320, width=320)
        self.canvas.pack()

        # ボードを長方形で表現
        for i in range(0, BOARD_SIZE):
            for j in range(0, BOARD_SIZE):
                self.canvas.create_rectangle(40 * i, 40 * j, 40 * (i + 1), 40 * (j + 1), fill="green")
        self.bind("<Button-1>", self.clicked)  # クリック操作を受け取る

        self.info = tk.StringVar()
        self.info.set("")
        self.label = tk.Label(self, textvariable=self.info)
        self.label.pack()
        self.button = tk.Button(self, text="Restart", command=self.refresh_board)
        self.button.pack()

        # ゲーム状況の初期化
        self.current_turn = None
        self.current_color = None
        self.raw_board = None
        self.current_movable = None
        self.opponent_movable = None

        # 初期配置
        self.refresh_board()

    def clicked(self, event):
        tag = self.point_to_tag(event.x, event.y)
        x_index, y_index = self.tag_to_index(tag)

        # 石が置ける場合のみ、石を置く・裏返す・ターンを変更する処理を行う
        if self.current_movable[x_index][y_index] != 0:
            self.put_piece(tag, self.current_color)
            self.reverse_piece(tag)
            self.change_turn()

    def point_to_tag(self, x, y):  # クリック座標をtagへ変換
        tag = X_TAG[x // 40] + Y_TAG[y // 40]
        return tag

    def index_to_tag(self, x, y):  # 二次元配列の座標をtagへ変換
        tag = X_TAG[x - 1] + Y_TAG[y - 1]
        return tag

    def tag_to_point(self, tag):  # 石描画のため、tagをGUI座標へ変換
        x = X_TAG.index(tag[0]) * 40
        y = Y_TAG.index(tag[1]) * 40
        return x, y

    def tag_to_index(self, tag):  # tagを二次元配列の座標へ変換
        x = X_TAG.index(tag[0]) + 1
        y = Y_TAG.index(tag[1]) + 1
        return x, y

    def color_to_str(self, color):  # 石描画のため、二次元配列用の数値を文字列へ変換
        if color == BLACK:
            str_color = "black"
        else:
            str_color = "white"
        return str_color

    def refresh_board(self):
        self.current_color = BLACK
        self.current_turn = 1

        # 盤面を初期化
        self.canvas.delete("piece_oval")
        self.raw_board = np.zeros((BOARD_SIZE + 2, BOARD_SIZE + 2), dtype=int)
        self.raw_board[0, :] = WALL
        self.raw_board[:, 0] = WALL
        self.raw_board[BOARD_SIZE + 1, :] = WALL
        self.raw_board[:, BOARD_SIZE + 1] = WALL
        self.put_piece("d4", BLACK)
        self.put_piece("e5", BLACK)
        self.put_piece("d5", WHITE)
        self.put_piece("e4", WHITE)

        # 石を置ける場所の判定
        self.current_movable = np.zeros((BOARD_SIZE + 2, BOARD_SIZE + 2), dtype=int)
        self.set_movable()

        # 両者パスによるゲームオーバー判定
        self.opponent_movable = np.zeros((BOARD_SIZE + 2, BOARD_SIZE + 2), dtype=int)
        self.set_movable(opponent=True)

        # labelへ現在のゲーム状況を反映
        self.set_info()

    def put_piece(self, tag, color):
        x_point, y_point = self.tag_to_point(tag)
        x_index, y_index = self.tag_to_index(tag)
        str_color = self.color_to_str(color)

        # 石を置く描画と併せ、二次元配列を更新
        self.canvas.create_oval(x_point, y_point, x_point + 40, y_point + 40, fill=str_color, tags="piece_oval")
        self.raw_board[x_index][y_index] = color

    def reverse_piece(self, tag):  # 石を裏返す描画
        x_index, y_index = self.tag_to_index(tag)
        str_color = self.color_to_str(self.current_color)

        for dir_index, reversible_dir_bit in zip(DIR_INDEX, REVERSIBLE_DIR_BIT):
            x_dir, y_dir = dir_index
            x_tmp = x_index + x_dir
            y_tmp = y_index + y_dir

            # 論理和で裏返せる方向を確認する
            if self.current_movable[x_index][y_index] | reversible_dir_bit == 0b11111111:
                while self.raw_board[x_tmp][y_tmp] == - self.current_color:
                    x_point_tmp, y_point_tmp = self.tag_to_point(self.index_to_tag(x_tmp, y_tmp))

                    # 石を裏返す描画と併せ、二次元配列を更新
                    self.canvas.create_oval(x_point_tmp, y_point_tmp, x_point_tmp + 40, y_point_tmp + 40,
                                            fill=str_color, tags="piece_oval")
                    self.raw_board[x_tmp][y_tmp] = self.current_color

                    x_tmp += x_dir
                    y_tmp += y_dir

    def change_turn(self):
        self.current_turn += 1
        self.current_color *= -1

        # 石を置ける場所の更新
        self.current_movable = np.zeros((BOARD_SIZE + 2, BOARD_SIZE + 2), dtype=int)
        self.set_movable()

        # 相手が石を置ける場所の更新
        self.opponent_movable = np.zeros((BOARD_SIZE + 2, BOARD_SIZE + 2), dtype=int)
        self.set_movable(opponent=True)

        # パス・ゲームオーバー判定
        self.check_pass()

        # labelへ現在のゲーム状況を反映
        self.set_info()

    def check_pass(self):
        if not self.current_movable.any():

            # 両者とも置ける場所がない場合ゲーム終了
            if not self.opponent_movable.any():
                messagebox.showinfo("game over", "お互いに置ける場所がありません。ゲーム終了です")
                return

            # 自分のみ置ける場所がない場合パス
            messagebox.showinfo("passed", "置ける場所がありません。パスします")
            self.current_color *= -1
            self.current_movable = np.zeros((BOARD_SIZE + 2, BOARD_SIZE + 2), dtype=int)
            self.set_movable()
            self.opponent_movable = np.zeros((BOARD_SIZE + 2, BOARD_SIZE + 2), dtype=int)
            self.set_movable(opponent=True)

    def set_movable(self, opponent=False):  # 各マスに石が置けるか判定を行う
        if not opponent:
            self.canvas.delete("movable_highlight")
            color = self.current_color
        else:
            color = - self.current_color

        for x_tag in X_TAG:
            for y_tag in Y_TAG:
                self.check_movable(x_tag + y_tag, color)

    def check_movable(self, tag, color):  # 石が置けるか判定を行い、置ける場所にはハイライトを付ける
        x_point, y_point = self.tag_to_point(tag)
        x_index, y_index = self.tag_to_index(tag)

        # 石が既に置かれている場合はスキップ
        if self.raw_board[x_index][y_index] != 0:
            return

        for dir_index, movable_dir_bit in zip(DIR_INDEX, MOVABLE_DIR_BIT):
            x_dir, y_dir = dir_index

            # 繰り返し処理用の仮変数
            x_tmp = x_index + x_dir
            y_tmp = y_index + y_dir
            count = 0

            while self.raw_board[x_tmp][y_tmp] == - color:
                x_tmp += x_dir
                y_tmp += y_dir
                count += 1

            else:
                if count != 0 and self.raw_board[x_tmp][y_tmp] == color:
                    if color == self.current_color:
                        self.canvas.create_rectangle(x_point, y_point, x_point + 40, y_point + 40,
                                                     fill="yellow", tags="movable_highlight")
                        # 裏返し時の処理簡略化のため、裏返せる方向を2進数で保管
                        self.current_movable[x_index][y_index] |= movable_dir_bit

                    else:  # 相手が石を置ける場所の判定を行う場合はハイライトは付けない
                        self.opponent_movable[x_index][y_index] |= movable_dir_bit

    def set_info(self):  # labelへ現在のゲーム状況を反映
        count_black = str(len(np.where(self.raw_board == 1)[0]))
        count_white = str(len(np.where(self.raw_board == -1)[0]))

        if self.current_color == BLACK:
            color = "黒"
        else:
            color = "白"

        self.info.set("黒：" + count_black + ", 白：" + count_white +
                      " Turn:" + str(self.current_turn) + ", " + color + "の手番です")


if __name__ == "__main__":
    app = App()
    app.mainloop()
