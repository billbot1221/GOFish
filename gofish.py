import streamlit as st
import random

# CSS styles
st.markdown("""
    <style>
    .card {
        display: inline-block;
        padding: 10px 15px;
        margin: 5px;
        border-radius: 8px;
        background: white;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        font-size: 20px;
    }
    .red-card {
        color: #D40000;
    }
    .black-card {
        color: #000000;
    }
    .game-title {
        color: #1E3D59;
        text-align: center;
        padding: 20px;
        font-size: 50px;
        font-weight: bold;
    }
    .status-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    .action-log {
        max-height: 200px;
        overflow-y: auto;
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 5px;
        background-color: #ffffff;
    }
    .player-action {
        padding: 8px;
        margin: 4px 0;
        border-radius: 4px;
        background-color: #e3f2fd;
    }
    .bot-action {
        padding: 8px;
        margin: 4px 0;
        border-radius: 4px;
        background-color: #fff3e0;
    }
    </style>
    """, unsafe_allow_html=True)


def display_card(card):
    """
    Display a card with appropriate styling based on suit
    """
    rank, suit = card
    card_class = "red-card" if suit in ['♥', '♦'] else "black-card"
    return f'<span class="card {card_class}">{rank}{suit}</span>'


def init_game():
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False
    if 'deck' not in st.session_state:
        st.session_state.deck = [(rank, suit)
                                 for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
                                 for suit in ['♠', '♣', '♥', '♦']]
        random.shuffle(st.session_state.deck)

    if 'players' not in st.session_state:
        st.session_state.players = [
            {"hand": [], "books": []} for _ in range(4)
        ]
        for _ in range(5):
            for player in st.session_state.players:
                if st.session_state.deck:
                    player["hand"].append(st.session_state.deck.pop())

    if 'current_turn' not in st.session_state:
        st.session_state.current_turn = 0

    if 'action_log' not in st.session_state:
        st.session_state.action_log = []
        st.session_state.game_over = False


def check_for_books(hand):
    books = []
    ranks = {}
    for card in hand:
        rank = card[0]
        if rank not in ranks:
            ranks[rank] = []
        ranks[rank].append(card)

    for rank, cards in ranks.items():
        if len(cards) == 4:
            books.append(cards)
            for card in cards:
                hand.remove(card)

    return books


def handle_bot_turn(bot_idx):
    bot_hand = st.session_state.players[bot_idx]["hand"]
    if not bot_hand:
        return

    target_rank = random.choice(bot_hand)[0]
    target_player = random.choice([i for i in range(4) if i != bot_idx])
    target_hand = st.session_state.players[target_player]["hand"]

    action_message = f"Player {bot_idx + 1} asks {'you' if target_player == 0 else f'Player {target_player + 1}'} for {target_rank}s"

    cards_found = []
    for card in target_hand[:]:
        if card[0] == target_rank:
            cards_found.append(card)
            target_hand.remove(card)
            bot_hand.append(card)

    if cards_found:
        action_message += f" and receives {len(cards_found)} card(s)!"
    else:
        if st.session_state.deck:
            drawn_card = st.session_state.deck.pop()
            bot_hand.append(drawn_card)
            action_message += " - Go fish!"
        else:
            action_message += " - No cards left in deck!"

    new_books = check_for_books(bot_hand)
    if new_books:
        action_message += f"\nPlayer {bot_idx + 1} completed {len(new_books)} book(s)!"
        st.session_state.players[bot_idx]["books"].extend(new_books)

    st.session_state.action_log.append(("bot", action_message))


def check_win_condition():
    """
    Check if the game is over and determine the winner(s)
    """
    if st.session_state.game_over:
        return

    all_hands_empty = all(not player["hand"] for player in st.session_state.players)

    if all_hands_empty and not st.session_state.deck:
        st.session_state.game_over = True

        # Count books for each player
        scores = [(i + 1, len(player["books"])) for i, player in enumerate(st.session_state.players)]
        max_books = max(score[1] for score in scores)
        winners = [f"Player {score[0]}" for score in scores if score[1] == max_books]

        # Display winners and scores
        st.markdown("### 🎉 Game Over!")
        if len(winners) > 1:
            st.markdown(f"🏆 It's a tie between {', '.join(winners)} with {max_books} books!")
        else:
            st.markdown(f"🏆 {winners[0]} wins with {max_books} books!")

        st.markdown("### 📊 Final Scores:")
        for player, books in scores:
            st.markdown(f"Player {player}: {books} books")

def go_fish_game():
    # Add Help & Rules dropdown section
    with st.expander("📝 Help & Rules", expanded=False):
        st.markdown("### How to Play Go Fish:")
        st.markdown("""
            - The game is played with 4 players. You are Player 1.
            - Each player is dealt 5 cards, and the remaining cards form the deck.
            - Your goal is to collect books (4 cards of the same rank).
            - **On Your Turn:** 
                - Choose another player to ask for a specific rank card that you have in your hand.
                - If the other player has cards of that rank, they must give them to you.
                - If not, you "Go Fish" and draw a card from the deck.
            - If you collect all 4 cards of a rank, a "book" is formed and removed from your hand.
        """)
        st.markdown("### Game Controls:")
        st.markdown("""
            - Use the **Ask for card** button to request cards from another player.
            - If it's not your turn, click the **Continue (Bot's turn)** button to let the bots take their turns.
            - At any point, you can restart the game by clicking the **New Game** button.
        """)
        st.markdown("### Winning:")
        st.markdown("""
            - The game ends when all hands are empty, and there are no more cards in the deck.
            - The player with the most books wins the game.
            - If there is a tie, the players with the most books share the victory.
        """)
    st.markdown('<h1 class="game-title">🎣 Go Fish 🎣</h1>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 New Game", use_container_width=True):
            for key in ['deck', 'players', 'current_turn', 'action_log']:
                if key in st.session_state:
                    del st.session_state[key]

    init_game()

    # Game status section
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="status-box">🎴 Cards in deck: {len(st.session_state.deck)}</div>',
                        unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="status-box">👤 Current turn: Player {st.session_state.current_turn + 1}</div>',
                        unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="book-display">📚 Your books: {len(st.session_state.players[0]["books"])}</div>',
                        unsafe_allow_html=True)

    # Display scores for all players
    st.markdown("### 📊 Scores:")
    score_cols = st.columns(4)
    for i, player in enumerate(st.session_state.players):
        with score_cols[i]:
            st.markdown(f'<div class="status-box">Player {i + 1}: {len(player["books"])} books</div>',
                        unsafe_allow_html=True)

    # Display player's hand
    st.markdown("### Your Hand:")
    player_hand = st.session_state.players[0]["hand"]
    if player_hand:
        cards_html = " ".join(display_card(card) for card in player_hand)
        st.markdown(f'<div style="margin: 20px 0;">{cards_html}</div>', unsafe_allow_html=True)

    # Action Log in expandable section
    with st.expander("📜 Game Action Log", expanded=False):
        if st.session_state.action_log:
            for action_type, message in st.session_state.action_log:
                css_class = "player-action" if action_type == "player" else "bot-action"
                icon = "👤" if action_type == "player" else "🤖"
                st.markdown(f'<div class="{css_class}">{icon} {message}</div>', unsafe_allow_html=True)
        else:
            st.write("No actions yet")

    # Game controls section
    if st.session_state.current_turn == 0:
        col1, col2 = st.columns(2)
        with col1:
            target_player = st.selectbox("🎯 Ask which player?", ["Player 2", "Player 3", "Player 4"])
            target_idx = int(target_player.split()[1]) - 1

        with col2:
            if player_hand:
                rank_to_ask = st.selectbox("🃏 Ask for which rank?",
                                           list(set(card[0] for card in player_hand)))

        if st.button("Ask for card", use_container_width=True):
            target_hand = st.session_state.players[target_idx]["hand"]
            cards_found = []

            action_message = f"You ask Player {target_idx + 1} for {rank_to_ask}s"

            for card in target_hand[:]:
                if card[0] == rank_to_ask:
                    cards_found.append(card)
                    target_hand.remove(card)
                    player_hand.append(card)

            if cards_found:
                action_message += f" and receive {len(cards_found)} card(s)!"
                new_books = check_for_books(player_hand)
                if new_books:
                    st.session_state.players[0]["books"].extend(new_books)
                    action_message += f"\nYou completed {len(new_books)} book(s)!"
            else:
                if st.session_state.deck:
                    drawn_card = st.session_state.deck.pop()
                    player_hand.append(drawn_card)
                    action_message += f" - Go fish! You drew {drawn_card[0]}{drawn_card[1]}"

                    new_books = check_for_books(player_hand)
                    if new_books:
                        st.session_state.players[0]["books"].extend(new_books)
                        action_message += f"\nYou completed {len(new_books)} book(s)!"
                else:
                    action_message += " - No cards left in the deck!"

            st.session_state.action_log.append(("player", action_message))
            st.session_state.current_turn = (st.session_state.current_turn + 1) % 4
            check_win_condition()
            st.rerun()

    else:
        if st.button("🤖 Continue (Bot's turn)", use_container_width=True):
            handle_bot_turn(st.session_state.current_turn)
            st.session_state.current_turn = (st.session_state.current_turn + 1) % 4
            check_win_condition()
            st.rerun()


if __name__ == "__main__":
    go_fish_game()
