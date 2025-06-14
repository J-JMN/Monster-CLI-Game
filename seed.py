import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Player, MonsterSpecies, PlayerMonster, Achievement, PlayerAchievement

engine = create_engine('sqlite:///monster_game.db')
Session = sessionmaker(bind=engine) 
session = Session()

TYPE_EFFECTIVENESS = {
    'Fire': {'strong_against': ['Grass', 'Ice'], 'weak_against': ['Water', 'Rock']},
    'Water': {'strong_against': ['Fire', 'Rock'], 'weak_against': ['Grass', 'Electric']},
    'Grass': {'strong_against': ['Water', 'Rock'], 'weak_against': ['Fire', 'Ice']},
    'Electric': {'strong_against': ['Water'], 'weak_against': ['Rock']},
    'Ice': {'strong_against': ['Grass'], 'weak_against': ['Fire']},
    'Rock': {'strong_against': ['Fire', 'Electric'], 'weak_against': ['Water', 'Grass']},
    'Normal': {'strong_against': [], 'weak_against': []},
}

RARITY_CATCH_CHANCE = {
    'Common': 0.8,
    'Uncommon': 0.6,
    'Rare': 0.3,
    'Epic': 0.2,
    'Legendary': 0.1
}


def calculate_catch_rate(species_rarity, player_level):
    base_chance = RARITY_CATCH_CHANCE.get(species_rarity, 0.1)
    level_bonus = min(player_level * 0.005, 0.20)
    return min(base_chance + level_bonus, 1.0)

def catch_monster(player_id, species_id):
    player = session.query(Player).get(player_id)
    species = session.query(MonsterSpecies).get(species_id)

    if not player or not species:
        print("Player or species not found.")
        return False

    catch_chance = calculate_catch_rate(species.rarity, player.level)
    
    if random.random() < catch_chance:
        new_monster = PlayerMonster(
            owner=player,
            species=species,
            nickname=species.name,
            current_hp=species.base_hp 
        )
        session.add(new_monster)
        session.commit()
        print(f"{player.username} successfully caught a {species.name}!")
        return True
    else:
        print(f"The {species.name} escaped from {player.username}!")
        return False

def level_up_monster(monster_id):
    monster = session.query(PlayerMonster).get(monster_id)
    if not monster:
        return {}

    monster.level += 1
    new_stats = {
        'level': monster.level,
        'hp': monster.species.base_hp + (monster.level * 5),
        'attack': monster.species.base_attack + (monster.level * 2),
        'defense': monster.species.base_defense + (monster.level * 2),
    }
    monster.current_hp = new_stats['hp'] 
    
    session.commit()
    print(f"{monster.nickname} grew to level {monster.level}!")
    return new_stats

def get_player_collection(player_id):
    player = session.query(Player).get(player_id)
    if not player:
        return []
    return player.monsters

def seed_database():
    session.query(PlayerAchievement).delete()
    session.query(Achievement).delete()
    session.query(PlayerMonster).delete()
    session.query(MonsterSpecies).delete()
    session.query(Player).delete()
    session.commit()
    print("Cleared existing data.")

    monster_species_data = [
        {'name': 'InfernoPup', 'monster_type': 'Fire', 'rarity': 'Common', 'base_hp': 40, 'base_attack': 60, 'base_defense': 45},
        {'name': 'AquaOtter', 'monster_type': 'Water', 'rarity': 'Common', 'base_hp': 55, 'base_attack': 45, 'base_defense': 55},
        {'name': 'LeafyRaptor', 'monster_type': 'Grass', 'rarity': 'Common', 'base_hp': 45, 'base_attack': 55, 'base_defense': 50},
        {'name': 'VoltMite', 'monster_type': 'Electric', 'rarity': 'Common', 'base_hp': 35, 'base_attack': 65, 'base_defense': 40},
        {'name': 'RockGolem', 'monster_type': 'Rock', 'rarity': 'Uncommon', 'base_hp': 70, 'base_attack': 50, 'base_defense': 80},
        {'name': 'BlazeLion', 'monster_type': 'Fire', 'rarity': 'Uncommon', 'base_hp': 60, 'base_attack': 80, 'base_defense': 60},
        {'name': 'TidalSerpent', 'monster_type': 'Water', 'rarity': 'Uncommon', 'base_hp': 75, 'base_attack': 65, 'base_defense': 70},
        {'name': 'ForestGuardian', 'monster_type': 'Grass', 'rarity': 'Rare', 'base_hp': 80, 'base_attack': 70, 'base_defense': 90},
        {'name': 'ThunderStallion', 'monster_type': 'Electric', 'rarity': 'Rare', 'base_hp': 70, 'base_attack': 90, 'base_defense': 65},
        {'name': 'Frostfang', 'monster_type': 'Ice', 'rarity': 'Rare', 'base_hp': 65, 'base_attack': 85, 'base_defense': 70},
        {'name': 'MagmaWurm', 'monster_type': 'Fire', 'rarity': 'Epic', 'base_hp': 90, 'base_attack': 110, 'base_defense': 80},
        {'name': 'AbyssKraken', 'monster_type': 'Water', 'rarity': 'Epic', 'base_hp': 120, 'base_attack': 90, 'base_defense': 100},
        {'name': 'TerraTitan', 'monster_type': 'Rock', 'rarity': 'Epic', 'base_hp': 100, 'base_attack': 80, 'base_defense': 130},
        {'name': 'ChronoWing', 'monster_type': 'Normal', 'rarity': 'Epic', 'base_hp': 85, 'base_attack': 95, 'base_defense': 85},
        {'name': 'SolarPhoenix', 'monster_type': 'Fire', 'rarity': 'Legendary', 'base_hp': 100, 'base_attack': 130, 'base_defense': 90},
        {'name': 'LunarLeviathan', 'monster_type': 'Water', 'rarity': 'Legendary', 'base_hp': 140, 'base_attack': 100, 'base_defense': 110},
        {'name': 'GigaWyrm', 'monster_type': 'Grass', 'rarity': 'Legendary', 'base_hp': 110, 'base_attack': 110, 'base_defense': 120},
        {'name': 'StormDjinn', 'monster_type': 'Electric', 'rarity': 'Legendary', 'base_hp': 90, 'base_attack': 140, 'base_defense': 80},
        {'name': 'GlacialBehemoth', 'monster_type': 'Ice', 'rarity': 'Legendary', 'base_hp': 130, 'base_attack': 90, 'base_defense': 130},
        {'name': 'StoneheartGiant', 'monster_type': 'Rock', 'rarity': 'Legendary', 'base_hp': 100, 'base_attack': 100, 'base_defense': 150},
    ]

    for data in monster_species_data:
        species = MonsterSpecies(**data)
        session.add(species)
    session.commit()
    print("Seeded Monster Species.")

    player1 = Player(username='AshK', level=5, money=500)
    player2 = Player(username='MistyW', level=3, money=350)
    player3 = Player(username='BrockR', level=4, money=400)
    session.add_all([player1, player2, player3])
    session.commit()
    print("Seeded Players.")

    catch_monster(player1.id, 1) 
    catch_monster(player1.id, 4) 

    catch_monster(player2.id, 2) 

    catch_monster(player3.id, 5)
    print("Seeded initial player monsters.")

    achievements_data = [
        {'name': 'First Catch', 'description': 'Successfully catch your first monster.'},
        {'name': 'Collector', 'description': 'Own 5 different species of monsters.'},
        {'name': 'Master Collector', 'description': 'Own 15 different species of monsters.'},
        {'name': 'First Win', 'description': 'Win your first battle against another player.'},
        {'name': 'Hot Streak', 'description': 'Win 5 battles in a row.'},
        {'name': 'Rarity Hunter', 'description': 'Catch a Rare monster.'},
        {'name': 'Epic Encounter', 'description': 'Catch an Epic monster.'},
        {'name': 'Legendary Tamer', 'description': 'Catch a Legendary monster.'}
    ]

    for data in achievements_data:
        achievement = Achievement(**data)
        session.add(achievement)
    session.commit()
    print("Seeded Achievements.")
    
    first_catch_achievement = session.query(Achievement).filter_by(name='First Catch').one()
    player_achievement_link = PlayerAchievement(player=player1, achievement=first_catch_achievement)
    session.add(player_achievement_link)
    session.commit()
    print("Awarded an initial achievement.")


if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Database tables dropped and recreated.")
    
    seed_database()
    
    print("\n--- Example Function Calls ---")
    
    test_player = session.query(Player).filter_by(username='AshK').one()
    
    print(f"\n{test_player.username}'s Collection:")
    collection = get_player_collection(test_player.id)
    for monster in collection:
        print(f"- {monster.nickname} (Lvl: {monster.level}, Species: {monster.species.name})")

    if collection:
        monster_to_level_up = collection[0]
        print(f"\nLeveling up {monster_to_level_up.nickname}...")
        level_up_monster(monster_to_level_up.id)
        updated_monster = session.query(PlayerMonster).get(monster_to_level_up.id)
        print(f"{updated_monster.nickname} is now level {updated_monster.level}.")
    
    print("\nAttempting to catch a rare monster...")
    catch_monster(test_player.id, 10) 

    print(f"\n{test_player.username}'s Final Collection:")
    final_collection = get_player_collection(test_player.id)
    for monster in final_collection:
        print(f"- {monster.nickname} (Lvl: {monster.level}, Species: {monster.species.name})")


    session.close()
    print("\nDatabase seeding complete.")