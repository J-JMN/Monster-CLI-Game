from models import Session, Player, PlayerMonster, Battle, Trade
import random
from datetime import datetime 

def create_battle(player1_id, player2_id=None):
    session = Session()

    battle = Battle(
        player1_id=player1_id,
        player2_id=player2_id,
        turns_taken=0
    )
    session.add(battle)
    session.commit()
    session.refresh(battle)

    print(f"New battle created! Battle ID: {battle.id}")
    return battle

def calculate_damage(attacker_stats, defender_stats, move_power, type_effectiveness):
  
    attack = attacker_stats.get("attack", 10)
    defense = defender_stats.get("defense", 10)
    multiplier = type_effectiveness
  
    if defense == 0:
        defense = 1

    base_damage = ((attack / defense) * move_power) * multiplier

    final_damage = int(base_damage + random.randint(-3, 3))

    return max(1, final_damage)  

def execute_turn(battle_id, attacker_monster_id, defender_monster_id, move):
    session = Session()
    
    battle = session.query(Battle).get(battle_id)
    attacker = session.query(PlayerMonster).get(attacker_monster_id)
    defender = session.query(PlayerMonster).get(defender_monster_id)

    move_power = {
        "attack": 10,
        "special": 15,
        "defend": 0
    }.get(move.lower(), 5)

    type_chart = {
        "Fire": {"Grass": 2.0, "Water": 0.5},
        "Water": {"Fire": 2.0, "Grass": 0.5},
        "Grass": {"Water": 2.0, "Fire": 0.5}
    }

    attacker_type = attacker.species.monster_type
    defender_type = defender.species.monster_type
    type_multiplier = type_chart.get(attacker_type, {}).get(defender_type, 1.0)

    attacker_stats = {
        "attack": attacker.species.base_attack,
        "defense": attacker.species.base_defense
    }
    defender_stats = {
        "attack": defender.species.base_attack,
        "defense": defender.species.base_defense
    }

    if move.lower() == "defend":
        result = {
            "action": "defend",
            "message": f"{attacker.nickname} defends and reduces incoming damage next turn!",
            "damage": 0
        }
    else:
        damage = calculate_damage(attacker_stats, defender_stats, move_power, type_multiplier)
        defender.current_hp = max(0, defender.current_hp - damage)

        result = {
            "action": move,
            "attacker": attacker.nickname,
            "defender": defender.nickname,
            "damage": damage,
            "new_defender_hp": defender.current_hp,
            "type_multiplier": type_multiplier,
            "message": f"{attacker.nickname} used {move}! {defender.nickname} took {damage} damage."
        }

    battle.turns_taken += 1
    session.commit()
    return result

def check_battle_end(battle_id):
    session = Session()
    battle = session.query(Battle).get(battle_id)

    player1_monsters = session.query(PlayerMonster).filter_by(player_id=battle.player1_id).all()
    player2_monsters = session.query(PlayerMonster).filter_by(player_id=battle.player2_id).all()

    all_p1_fainted = all(m.current_hp <= 0 for m in player1_monsters)
    all_p2_fainted = all(m.current_hp <= 0 for m in player2_monsters)

    if all_p1_fainted:
        battle.winner_id = battle.player2_id
        session.commit()
        return True, battle.player2_id

    if all_p2_fainted:
        battle.winner_id = battle.player1_id
        session.commit()
        return True, battle.player1_id

    return False, None


def apply_status_effects(monster_id, effect_type):
    session = Session()
    monster = session.query(PlayerMonster).get(monster_id)

    if effect_type == "heal":
        max_hp = monster.species.base_hp
        healed = min(max_hp, monster.current_hp + 10)
        monster.current_hp = healed

    elif effect_type == "burn":
        monster.current_hp = max(0, monster.current_hp - 5)

    elif effect_type == "boost":
        monster.current_experience += 10  # Temporary boost

    session.commit()


def propose_trade(from_player, to_player, offered_monsters, requested_monsters):
    session = Session()

    trades = []
    for offer_id, request_id in zip(offered_monsters, requested_monsters):
        trade = Trade(
            proposing_player_id=from_player,
            accepting_player_id=to_player,
            proposing_player_monster_id=offer_id,
            accepting_player_monster_id=request_id,
            status="proposed",
            trade_timestamp=datetime.now()
        )
        session.add(trade)
        trades.append(trade)

    session.commit()
    return trades


def calculate_battle_rewards(winner_id, battle_difficulty):
    session = Session()
    winner = session.query(Player).get(winner_id)

    difficulty_multiplier = {
        "easy": 1,
        "medium": 2,
        "hard": 3
    }.get(battle_difficulty.lower(), 1)

    xp_gain = 20 * difficulty_multiplier
    money_gain = 50 * difficulty_multiplier

    winner.experience += xp_gain
    winner.money += money_gain

    session.commit()
    return xp_gain, money_gain


def create_ai_opponent(difficulty_level):
    fake_names = {
        "easy": "Bot-EZ",
        "medium": "Bot-MD",
        "hard": "Bot-EX"
    }
    session = Session()
    bot = Player(username=fake_names.get(difficulty_level.lower(), "Bot"), level=1)
    session.add(bot)
    session.commit()
    session.refresh(bot)

    return {
        "id": bot.id,
        "username": bot.username
    }
