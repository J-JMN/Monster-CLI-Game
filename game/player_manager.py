from models import Session, Player

def create_player(username):
    session = Session()

    existing = session.query(Player).filter_by(username=username).first()
    if existing:
        return f"Username '{username}' already exists."

    player = Player(username=username, level=1, experience=0, money=100)
    session.add(player)
    session.commit()
    session.refresh(player)

    return f"Player '{username}' created successfully! ID: {player.id}"

def login_player(username):
    session = Session()
    player = session.query(Player).filter_by(username=username).first()
    
    if not player:
        return f"No player found with username '{username}'."
    
    return player

def update_player_xp(player_id, xp_earned):
    session = Session()
    player = session.query(Player).get(player_id)

    if not player:
        return f"Player ID {player_id} not found."

    player.experience += xp_earned

    while player.experience >= 100 * player.level:
        player.experience -= 100 * player.level
        player.level += 1
        print(f"{player.username} leveled up! Now level {player.level}")

    session.commit()
    return f"{player.username} now has {player.experience} XP and is level {player.level}"
