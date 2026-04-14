from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

class MinesweeperGame:
    def __init__(self, difficulty='medium'):
        # 根据难度设置参数
        if difficulty == 'easy':
            self.rows, self.cols, self.mines = 8, 8, 10
        elif difficulty == 'hard':
            self.rows, self.cols, self.mines = 16, 16, 40
        else:  # medium (default)
            self.rows, self.cols, self.mines = 10, 10, 15

        self.board = []
        self.game_over = False
        self.win = False
        self.init_board()

    def init_board(self):
        """Initialize game board with mines and numbers"""
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        # Place mines randomly
        mine_positions = set()
        while len(mine_positions) < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            mine_positions.add((row, col))

        for row, col in mine_positions:
            self.board[row][col] = -1
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols and self.board[nr][nc] != -1:
                        self.board[nr][nc] += 1

    def get_board_state(self, revealed=None):
        """Return the current board state with revealed cells"""
        if revealed is None:
            revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]

        board_state = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                if revealed[i][j] or self.game_over or self.win:
                    if self.board[i][j] == -1:
                        row.append('💣')  # 地雷
                    elif self.board[i][j] == 0:
                        row.append('')    # 空白格子
                    else:
                        row.append(str(self.board[i][j]))  # 数字
                else:
                    row.append('')  # 未揭示的格子
            board_state.append(row)

        return board_state

game = MinesweeperGame()

@app.route('/')
def index():
    return render_template('index.html', board=game.board, rows=game.rows, cols=game.cols)

@app.route('/reveal', methods=['POST'])
def reveal_cell():
    data = request.get_json()
    row = data.get('row')
    col = data.get('col')

    if game.board[row][col] == -1:
        game.game_over = True
        return jsonify({'status': 'lost', 'board': game.board})

    # 跟踪已揭示的格子
    revealed = [[False for _ in range(game.cols)] for _ in range(game.rows)]

    def reveal(row, col):
        # 边界检查
        if row < 0 or row >= game.rows or col < 0 or col >= game.cols:
            return
        # 如果已经揭示过或游戏结束则返回
        if revealed[row][col] or game.game_over:
            return

        revealed[row][col] = True

        # 如果是空白格子，递归揭示周围
        if game.board[row][col] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    reveal(row + dr, col + dc)

    # 开始揭示
    reveal(row, col)

    # 检查是否获胜
    total_safe = game.rows * game.cols - game.mines
    revealed_count = sum(sum(row) for row in revealed)
    if revealed_count >= total_safe:
        game.win = True
        return jsonify({
            'status': 'won',
            'board': game.get_board_state(revealed)
        })

    return jsonify({
        'status': 'continue',
        'board': game.get_board_state(revealed)
    })

@app.route('/new_game', methods=['POST'])
def new_game():
    global game
    data = request.get_json()
    difficulty = data.get('difficulty', 'medium')
    game = MinesweeperGame(difficulty=difficulty)
    return jsonify({'status': 'new_game', 'board': game.board, 'rows': game.rows, 'cols': game.cols})

if __name__ == '__main__':
    app.run(debug=True)
