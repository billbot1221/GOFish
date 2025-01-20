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
    }x
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

# Check if the game is over and calculate the winner
def check_for_winner():
    # Game ends if the deck is empty and all hands are empty
    if len(st.session_state.deck) == 0 and all(len(player["hand"]) == 0 for player in st.session_state.players):
        # Calculate scores based on books
        scores = [(i, len(player["books"])) for i, player in enumerate(st.session_state.players)]
        scores.sort(key=lambda x: x[1], reverse=True)  # Sort players by the number of books (descending)

        # Find the player(s) with the most books
        top_score = scores[0][1]
        winners = [f"Player {i + 1}" for i, score in scores if score == top_score]

        # Build a winner message
        if len(winners) == 1:
            winner_message = f"{winners[0]} wins with {top_score} books!"
        else:
            winner_message = f"{' and '.join(winners)} tie with {top_score} books!"

        # Log the result and display scores
        st.session_state.action_log.append(("game", f"🎉 Game Over! {winner_message}"))
        st.session_state.action_log.append(("game", f"📊 Final Scores: " +
                                             ", ".join([f"Player {i + 1}: {score} books" for i, score in scores])))

        return True  # Game is over
    return False  # Game is not over

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


def go_fish_game():
    st.markdown('<h1 class="game-title">🎣 Go Fish 🎣</h1>', unsafe_allow_html=True)

    if st.button("🔄 New Game", use_container_width=True):
        for key in ['deck', 'players', 'current_turn', 'action_log']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    init_game()

    # Check if the game is over
    if check_for_winner():
        st.markdown('<div class="game-over">🎉 Game Over! See action log for results.</div>', unsafe_allow_html=True)
        with st.expander("📜 Game Action Log", expanded=True):
            for action_type, message in st.session_state.action_log:
                css_class = "player-action" if action_type == "player" else "bot-action"
                icon = "👤" if action_type == "player" else "🤖"
                st.markdown(f'<div class="{css_class}">{icon} {message}</div>', unsafe_allow_html=True)
        return  # End game here

    st.markdown("### Current Status")
    st.markdown(f"📚 Your Books: {len(st.session_state.players[0]['books'])}")
    st.markdown("Your Hand:")
    player_hand = st.session_state.players[0]["hand"]
    if player_hand:
        cards_html = " ".join([f"<span>{card[0]}{card[1]}</span>" for card in player_hand])
        st.markdown(cards_html, unsafe_allow_html=True)

    # Proceed to the next turn
    st.button("🤖 Next Turn")
    st.rerun()



if __name__ == "__main__":
    go_fish_game()
