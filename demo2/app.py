from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# 扑克牌花色和点数
SUITS = ['♥', '♦', '♣', '♠']
RANKS = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
SPECIAL = ['小王', '大王']

class LandlordGame:
    def __init__(self):
        self.players = [[], [], []]  # 三个玩家的手牌
        self.landlord_cards = []     # 地主牌
        self.current_player = 0      # 当前出牌玩家
        self.last_play = []          # 上次出的牌
        self.game_started = False

    def deal_cards(self):
        """发牌"""
        deck = []
        # 生成普通牌
        for suit in SUITS:
            for rank in RANKS:
                deck.append(f"{suit}{rank}")
        # 添加王牌
        deck.extend(SPECIAL)
        # 洗牌
        random.shuffle(deck)

        # 发牌(每人17张)
        for i in range(51):
            self.players[i % 3].append(deck.pop())

        # 剩余3张作为地主牌
        self.landlord_cards = deck
        self.game_started = True

game = LandlordGame()

@app.route('/')
def index():
    if not game.game_started:
        game.deal_cards()
    return render_template('index.html',
                         player_cards=game.players[0],
                         landlord_cards=game.landlord_cards)

@app.route('/play', methods=['POST'])
def play_cards():
    data = request.get_json()
    cards = data.get('cards', [])

    # 简单验证
    if not cards:
        return jsonify({'status': 'error', 'message': '请选择要出的牌'})

    # 更新游戏状态
    game.last_play = cards
    game.current_player = (game.current_player + 1) % 3

    return jsonify({
        'status': 'success',
        'last_play': game.last_play,
        'next_player': game.current_player
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
