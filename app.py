import streamlit as st
import random
from PIL import Image

st.set_page_config(
    page_title="ポーカー", 
    page_icon='png/red_joker.png' 
    )

# カードとデッキの初期化
def init_deck():
    suits = ['ハート', 'ダイヤ', 'クラブ', 'スペード']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'ジャック', 'クイーン', 'キング', 'エース']
    deck = [(rank, suit) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

# 手札の評価
def evaluate_hand(hand):
    # カードのランクとスーツを分けてリスト化
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'ジャック', 'クイーン', 'キング', 'エース']
    rank_values = {rank: index for index, rank in enumerate(ranks, start=2)}
    hand_ranks = sorted([rank_values[card[0]] for card in hand], reverse=True)
    suits = [card[1] for card in hand]
    
    # 各ランクの出現回数を数える
    rank_counts = {rank: hand_ranks.count(rank) for rank in hand_ranks}
    counts = list(rank_counts.values())

    # フラッシュの判定
    is_flush = len(set(suits)) == 1

    # ストレートの判定
    is_straight = len(set(hand_ranks)) == 5 and (max(hand_ranks) - min(hand_ranks) == 4)

    # ロイヤルフラッシュの判定
    is_royal = is_flush and is_straight and max(hand_ranks) == rank_values['A']

    # ハンドのランクを数値で評価（大きいほど強い）
    if is_royal:
        return (10, "ロイヤルフラッシュ", hand_ranks)
    elif is_straight and is_flush:
        return (9, "ストレートフラッシュ", hand_ranks)
    elif 4 in counts:
        return (8, "フォーカード", hand_ranks)
    elif 3 in counts and 2 in counts:
        return (7, "フルハウス", hand_ranks)
    elif is_flush:
        return (6, "フラッシュ", hand_ranks)
    elif is_straight:
        return (5, "ストレート", hand_ranks)
    elif 3 in counts:
        return (4, "スリーカード", hand_ranks)
    elif counts.count(2) == 2:
        return (3, "2ペア", hand_ranks)
    elif 2 in counts:
        return (2, "1ペア", hand_ranks)
    else:
        return (1, "ハイカード", hand_ranks)

# Streamlitセッションステートの初期化
if 'deck' not in st.session_state:
    st.session_state['deck'] = init_deck()
    
if 'player_hand' not in st.session_state:
    st.session_state['player_hand'] = [st.session_state['deck'].pop() for _ in range(5)]

if 'opponent_hand' not in st.session_state:
    st.session_state['opponent_hand'] = [st.session_state['deck'].pop() for _ in range(5)]

st.title('ポーカー')

# プレイヤーの手札と交換機能
st.write('自分の手札')
col1, col2, col3, col4, col5 = st.columns(5)
columns = [col1, col2, col3, col4, col5]
indexes_to_replace = []

for i, card in enumerate(st.session_state['player_hand']):
    # カードのランクとスートを元に画像ファイル名を生成
    card_image_filename = f"{card[0].lower()}_of_{card[1].lower()}.png"
    image_path = f'png/{card_image_filename}'

    # PILライブラリを使用して画像を読み込む
    image = Image.open(image_path)

    with columns[i]:
        # カードの画像を表示
        st.image(image, width=120, caption=f"{card[1]}の{card[0].upper()}")

        # カード交換のチェックボックスを表示
        if st.checkbox('交換', key=i):
            indexes_to_replace.append(i)

# カードの交換処理
if st.button('カードを交換'):
    for index in indexes_to_replace:
        st.session_state['player_hand'][index] = st.session_state['deck'].pop()

    # 交換後の手札を保存
    st.session_state['player_hand_after_exchange'] = st.session_state['player_hand']

    # 手札を交換した後は、すぐには勝敗を判定せず、交換後の手札を表示する
    st.session_state['show_result'] = False

# プレイヤーの手札表示関数
def display_player_hand(hand, key_prefix=''):
    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]

    for i, card in enumerate(hand):
        card_image_filename = f"{card[0].lower()}_of_{card[1].lower()}.png"
        image_path = f'png/{card_image_filename}'
        image = Image.open(image_path)

        with columns[i]:
            # key 引数を削除
            st.image(image, width=120, caption=f"{card[1]}の{card[0].upper()}")

# 交換後の手札を表示
if 'player_hand_after_exchange' in st.session_state:
    st.write('交換後の手札')
    # 初期の手札表示を上書きする
    display_player_hand(st.session_state['player_hand_after_exchange'], 'after_exchange')

    # 「勝負」ボタンを表示
    if st.button('勝負'):
        st.session_state['show_result'] = True

# 勝敗の結果を表示
if st.session_state.get('show_result'):
    # 相手の手札の画像を表示
    st.write('相手の手札')
    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]

    for i, card in enumerate(st.session_state['opponent_hand']):
        card_image_filename = f"{card[0].lower()}_of_{card[1].lower()}.png"
        image_path = f'png/{card_image_filename}'
        image = Image.open(image_path)

        with columns[i]:
            st.image(image, width=120, caption=f"{card[1]}の{card[0].upper()}")

        # プレイヤーと相手の手札を評価
        st.session_state['player_evaluation'] = evaluate_hand(st.session_state['player_hand'])
        st.session_state['opponent_evaluation'] = evaluate_hand(st.session_state['opponent_hand'])

        # 結果の表示
        player_score, player_rank, _ = st.session_state['player_evaluation']
        opponent_score, opponent_rank, _ = st.session_state['opponent_evaluation']

    st.write(f"あなたの役: {player_rank}")
    st.write(f"相手の役: {opponent_rank}")

    # 勝敗の判定
    if player_score > opponent_score:
        st.success('あなたの勝ちです！')
    elif player_score < opponent_score:
        st.error('残念、あなたの負けです。')
    else:
        # ランクが同じ場合、カードの値によって勝敗を決定
        for player_card, opponent_card in zip(st.session_state['player_evaluation'][2], st.session_state['opponent_evaluation'][2]):
            if player_card > opponent_card:
                st.success('あなたの勝ちです！')
                break
            elif player_card < opponent_card:
                st.error('残念、あなたの負けです。')
                break
        else:
            st.warning('引き分けです。')