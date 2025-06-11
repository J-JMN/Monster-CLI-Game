import os
import random
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.text import Text
from rich.live import Live
from models import Base, Player, MonsterSpecies, PlayerMonster
from seed import TYPE_EFFECTIVENESS, calculate_catch_rate

current_player = None

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DB_PATH = os.path.join(BASE_DIR, "monster_game.db")
engine = create_engine(f"sqlite:///{DB_PATH}")
Session = sessionmaker(bind=engine)
session = Session()

console = Console()

def get_player_by_id(player_id):
    return session.query(Player).get(player_id)

def get_player_monster_by_id(monster_id):
    """
    🎯 Get Player's Monster by ID

    - Searches `current_player.monsters` by ID.
    - Returns monster or `None` if not found.
    - Used in trading logic.
    """

    return session.get(PlayerMonster, monster_id)

def calculate_monster_stats(monster):
    species = monster.species
    level = monster.level
    stats = {
        'max_hp': species.base_hp + (level * 5),
        'attack': species.base_attack + (level * 3),
        'defense': species.base_defense + (level * 2)
    }
    return stats

def print_welcome():
    welcome_panel = Panel(
        Text("Welcome to Monster World!", justify="center", style="bold magenta"),
        title="[bold cyan]Monster CLI Game[/bold cyan]",
        subtitle="[bold cyan]Created with Rich & SQLAlchemy[/bold cyan]",
        border_style="green"
    )
    console.print(welcome_panel)

def login_or_register():
    """
    🔐 Login or Register a Player

    - Prompts user to login or register.
    - Checks database for existing username.
    - If new, creates a player and commits.
    - Sets `current_player` globally for session use.
    """

    global current_player
    while current_player is None:
        console.print("\n[1] Login")
        console.print("[2] Register")
        choice = Prompt.ask("Choose an option", choices=["1", "2"])

        username = Prompt.ask("Enter your username").strip()
        if not username:
            console.print("[bold red]Username cannot be empty.[/bold red]")
            continue

        player = session.query(Player).filter_by(username=username).first()

        if choice == '1': 
            if player:
                current_player = player
                console.print(f"\nWelcome back, [bold blue]{current_player.username}[/bold blue]!")
            else:
                console.print("[bold red]Player not found. Please register.[/bold red]")
        
        elif choice == '2': 
         if player:
                 console.print("[bold yellow]Username already exists. Please try logging in or choose a different username.[/bold yellow]")
         else:
            try:
                current_player = Player(
                username=username,
                level=1,          
                money=100,        
                experience=0      
                )
                session.add(current_player)
                session.commit()  
                new_player = session.query(Player).filter_by(username=username).first()
                if new_player:
                    console.print(f"\nWelcome, [bold green]{current_player.username}[/bold green]! Your adventure begins!")
                else:
                    console.print("[bold red]Failed to create player account. Please try again.[/bold red]")
                    current_player = None
            except Exception as e:
                session.rollback()
                console.print(f"[bold red]Error creating account: {str(e)}[/bold red]")
                current_player = None
                
def view_collection():
    """
    📚 View Player's Monster Collection

    - Lists all monsters the player owns.
    - Shows nickname, species, level, HP, rarity.
    - Uses Rich Table for CLI visualization.
    """

    console.print(Panel(f"[bold green]{current_player.username}'s Monster Collection[/bold green]", expand=False))
    monsters = session.query(PlayerMonster).filter_by(player_id=current_player.id).all()

    if not monsters:
        console.print("[yellow]Your collection is empty. Go out and catch some monsters![/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=4)
    table.add_column("Nickname", style="cyan")
    table.add_column("Species", style="green")
    table.add_column("Type", style="white")
    table.add_column("Level", style="yellow")
    table.add_column("HP", style="red")
    table.add_column("Attack", style="bold red")
    table.add_column("Defense", style="bold blue")
    table.add_column("Rarity", style="magenta")

    for monster in monsters:
        stats = calculate_monster_stats(monster)
        table.add_row(
            str(monster.id),
            monster.nickname,
            monster.species.name,
            monster.species.monster_type,
            str(monster.level),
            f"{monster.current_hp}/{stats['max_hp']}",
            str(stats['attack']),
            str(stats['defense']),
            monster.species.rarity
        )
    console.print(table)

def view_profile():
    """
    📋 View Player Profile

    - Displays current player's username, level, experience, and money.
    - Uses Rich `console.rule()` for clean formatting.
    """

    panel_content = f"""[bold blue]Username[/bold blue]: {current_player.username}
[bold yellow]Level[/bold yellow]: {current_player.level}
[bold green]Money[/bold green]: ${current_player.money}
[bold magenta]Experience[/bold magenta]: {current_player.experience}"""
    
    console.print(Panel(panel_content, title=f"[bold cyan]{current_player.username}'s Profile[/bold cyan]", expand=False))

def attempt_catch():
    """
    🪤 Attempt to Catch a Wild Monster

    - Randomly selects a wild monster.
    - Displays stats and asks player to catch or flee.
    - Catch success is based on rarity and player's level.
    - Adds monster to player on success.
    - Provides outcome feedback with Rich visuals.
    """

    console.print("\nSearching for a wild monster...", style="italic cyan")
    time.sleep(1.5)

    rarity_weights = {'Common': 10, 'Uncommon': 5, 'Rare': 2, 'Epic': 1, 'Legendary': 0.5}
    all_species = session.query(MonsterSpecies).all()
    wild_monster_species = random.choices(
        all_species, 
        weights=[rarity_weights[s.rarity] for s in all_species], 
        k=1
    )[0]
    
    color = wild_monster_species.rarity.lower()
    console.print(Panel(
        f"A wild [bold {color}]{wild_monster_species.name}[/bold {color}] appears!\n"
        f"[dim]Rarity:[/dim] [bold {color}]{wild_monster_species.rarity}[/bold {color}]",
        title="[bold yellow]Encounter![/bold yellow]",
        border_style="yellow"
    ))


    catch_chance = calculate_catch_rate(wild_monster_species.rarity, current_player.level)
    console.print(f"Your chance to catch it is [bold]{catch_chance:.0%}[/bold].")
    
    choice = Prompt.ask("Attempt to catch it?", choices=["y", "n"], default="y")
    if choice == 'n':
        console.print(f"You let the {wild_monster_species.name} go.")
        return

    console.print("You throw a capture device...", style="italic")
    time.sleep(1)
    
    if random.random() < catch_chance:
        new_monster = PlayerMonster(
            owner=current_player,
            species=wild_monster_species,
            nickname=wild_monster_species.name,
            current_hp=wild_monster_species.base_hp
        )
        session.add(new_monster)
        session.commit()
        console.print(f"[bold green]Gotcha! {wild_monster_species.name} was caught![/bold green]")

    else:
        console.print("[bold red]Oh no! The monster broke free![/bold red]")

def render_xp_bar(current_xp, level):
    threshold = level * 10
    bar_length = 40
    fill_ratio = current_xp / threshold
    filled = int(bar_length * fill_ratio)
    empty = bar_length - filled
    bar = f"[bold cyan]|[/bold cyan]{'█' * filled}{' ' * empty}[bold cyan]|[/bold cyan]"
    return f"{bar} {current_xp}/{threshold} XP"

def get_type_effectiveness(attacker_type, defender_type):
    """
    🧮 Calculate Type Effectiveness

    - Returns damage multiplier based on attacker vs defender type.
    - Uses a dictionary-based matchup matrix.
    """

    if defender_type in TYPE_EFFECTIVENESS.get(attacker_type, {}).get('strong_against', []):
        return 1.5, "It's super effective! Elemental bonus damage!"
    elif defender_type in TYPE_EFFECTIVENESS.get(attacker_type, {}).get('weak_against', []):
        return 0.7, "It's not very effective, Elemental debuffer!"
    return 1.0, 

def start_battle():
    """
    ⚔️ Start a Wild Monster Battle

    - Allows player to choose one of their monsters.
    - Battles a random wild monster.
    - Turn-based damage system:
        - Attacker level, randomness, and type effectiveness.
    - Displays combat via Rich console.
    - Awards XP, money, and level-ups.
    """

    console.print(Panel("[bold red]Battle System (PvE)[/bold red]", expand=False))

    player_monsters = session.query(PlayerMonster).filter_by(player_id=current_player.id).all()
    if not player_monsters:
        console.print("[bold red]You have no monsters to battle with! Go catch some first.[/bold red]")
        return

    view_collection()
    chosen_id = IntPrompt.ask("Choose a monster to battle with (enter ID)")
    player_monster = get_player_monster_by_id(chosen_id)

    if not player_monster or player_monster.player_id != current_player.id:
        console.print("[bold red]Invalid selection.[/bold red]")
        return

    all_species = session.query(MonsterSpecies).all()
    opponent_species = random.choice(all_species)

    player_stats = calculate_monster_stats(player_monster)
    opponent_stats = {
        'max_hp': opponent_species.base_hp,
        'attack': opponent_species.base_attack,
        'defense': opponent_species.base_defense
    }
    opponent_hp = opponent_stats['max_hp']
    battle_summary = ""

    with Live(console=console, screen=False, auto_refresh=False) as live:
        turn = 0
        while player_monster.current_hp > 0 and opponent_hp > 0:
            turn += 1

            player_table = Table(title=f"Your {player_monster.nickname} ({player_monster.species.rarity})")
            player_table.add_column("Stat", style="cyan")
            player_table.add_column("Value", style="white")
            player_table.add_row("HP", f"[bold red]{player_monster.current_hp}/{player_stats['max_hp']}[/bold red]")

            opponent_table = Table(title=f"Wild {opponent_species.name} ({opponent_species.rarity})")
            opponent_table.add_column("Stat", style="cyan")
            opponent_table.add_column("Value", style="white")
            opponent_table.add_row("HP", f"[bold red]{opponent_hp}/{opponent_stats['max_hp']}[/bold red]")

            battle_panel = Panel(battle_summary, title=f"[bold yellow]Turn {turn}[/bold yellow]", border_style="red")

            main_table = Table(show_header=False, box=None, expand=True)
            main_table.add_row(player_table, opponent_table)
            main_table.add_row(battle_panel)

            live.update(main_table, refresh=True)
            time.sleep(1.0)

                        
            player_atk_type = player_monster.species.monster_type
            wild_def_type = opponent_species.monster_type
            player_multiplier, player_effectiveness_msg = get_type_effectiveness(player_atk_type, wild_def_type)

            base_damage = max(1, player_stats['attack'] - opponent_stats['defense'] // 2)
            damage_to_opponent = int(base_damage * player_multiplier)
            opponent_hp -= damage_to_opponent

            battle_summary = f"Your {player_monster.nickname} attacks! It deals [bold red]{damage_to_opponent} damage[/bold red]."
            if player_effectiveness_msg:
                battle_summary += f"\n[bold yellow]{player_effectiveness_msg}[/bold yellow]"

            live.update(main_table, refresh=True)
            time.sleep(1.5)

            if opponent_hp <= 0:
                break

            
            wild_atk_type = opponent_species.monster_type
            player_def_type = player_monster.species.monster_type
            wild_multiplier, wild_effectiveness_msg = get_type_effectiveness(wild_atk_type, player_def_type)

            base_damage = max(1, opponent_stats['attack'] - player_stats['defense'] // 2)
            damage_to_player = int(base_damage * wild_multiplier)
            player_monster.current_hp -= damage_to_player

            battle_summary += f"\nThe wild {opponent_species.name} attacks back! It deals [bold red]{damage_to_player} damage[/bold red]."
            if wild_effectiveness_msg:
                battle_summary += f"\n[bold red]{wild_effectiveness_msg}[/bold red]"

            live.update(main_table, refresh=True)
            time.sleep(1.5)


    if player_monster.current_hp > 0:
        console.print(Panel(
            f"[bold green]You defeated the wild {opponent_species.name} ({opponent_species.rarity})![/bold green]",
            border_style="green"
        ))

        exp_gain = opponent_species.base_hp // 2
        player_monster.current_experience += exp_gain
        current_player.experience += exp_gain

        leveled_up = False
        while player_monster.current_experience >= player_monster.level * 10:
            player_monster.current_experience -= player_monster.level * 10
            player_monster.level += 1
            leveled_up = True

        if leveled_up:
            player_monster.current_hp = player_monster.species.base_hp + (player_monster.level * 5)
            console.print(f"[bold yellow]Congratulations! {player_monster.nickname} leveled up to Level {player_monster.level}![/bold yellow]")
            console.print(f"[bold green]{player_monster.nickname} is now fully healed![/bold green]")
        else:
            max_hp = player_monster.species.base_hp + (player_monster.level * 5)
            player_monster.current_hp = min(player_monster.current_hp, max_hp)

        money_gain = opponent_species.base_attack // 5
        current_player.money += money_gain

        console.print(f"You earned [magenta]{exp_gain} EXP[/magenta] and [green]${money_gain}[/green]!")
        console.print(f"[bold cyan]{player_monster.nickname}'s XP:[/bold cyan] {render_xp_bar(player_monster.current_experience, player_monster.level)}")

    else:
        player_monster.current_hp = 0
        console.print(Panel(
            f"[bold red]Your {player_monster.nickname} has been injured! You rush to safety.[/bold red]",
            border_style="red"
        ))

    session.commit()


def trade_system():
    """
    🤝 Trade Monsters Between Players

    - Player selects another player.
    - Views both monster collections.
    - Trades one monster from each.
    - Confirms trade, transfers ownership, updates nickname.
    - Includes error handling and rollback safety.
    """

    console.print(Panel("[bold yellow]Trade System[/bold yellow]", expand=False))
    
    other_players = session.query(Player).filter(Player.id != current_player.id).all()
    if not other_players:
        console.print("[yellow]There are no other players to trade with yet.[/yellow]")
        return

    console.print("\n[bold cyan]Available Players:[/bold cyan]")
    player_table = Table(show_header=True, header_style="bold magenta")
    player_table.add_column("ID", style="dim", width=4)
    player_table.add_column("Username", style="cyan")
    player_table.add_column("Level", style="yellow")
    player_table.add_column("Monsters", style="green")
    
    for idx, player in enumerate(other_players, start=1):
        monster_count = session.query(PlayerMonster).filter_by(player_id=player.id).count()
        player_table.add_row(str(idx), player.username, str(player.level), str(monster_count))
    
    console.print(player_table)
    
    partner_idx = IntPrompt.ask("\nSelect a player to trade with (enter ID)", choices=[str(i) for i in range(1, len(other_players)+1)])
    trading_partner = other_players[int(partner_idx)-1]
    
    console.print(f"\n[bold]Trade between [cyan]{current_player.username}[/cyan] and [green]{trading_partner.username}[/green][/bold]")
    
    player_monsters = session.query(PlayerMonster).filter_by(player_id=current_player.id).all()
    partner_monsters = session.query(PlayerMonster).filter_by(player_id=trading_partner.id).all()
    
    if not player_monsters:
        console.print("[red]You have no monsters to trade![/red]")
        return
    if not partner_monsters:
        console.print(f"[red]{trading_partner.username} has no monsters to trade![/red]")
        return
    
    console.print(f"\n[bold cyan]Your Monsters:[/bold cyan]")
    player_monster_table = Table(show_header=True, header_style="bold magenta")
    player_monster_table.add_column("ID", style="dim", width=4)
    player_monster_table.add_column("Nickname", style="cyan")
    player_monster_table.add_column("Species", style="green")
    player_monster_table.add_column("Level", style="yellow")
    player_monster_table.add_column("Rarity", style="magenta")

    for monster in player_monsters:
        player_monster_table.add_row(
            str(monster.id),
            monster.nickname,
            monster.species.name,
            str(monster.level),
            monster.species.rarity
        )
    console.print(player_monster_table)
    
    your_monster_id = IntPrompt.ask("\nSelect a monster to trade (enter ID)", 
                                   choices=[str(m.id) for m in player_monsters])
    your_monster = get_player_monster_by_id(your_monster_id)
    
    console.print(f"\n[bold green]{trading_partner.username}'s Monsters:[/bold green]")
    partner_monster_table = Table(show_header=True, header_style="bold magenta")
    partner_monster_table.add_column("ID", style="dim", width=4)
    partner_monster_table.add_column("Nickname", style="cyan")
    partner_monster_table.add_column("Species", style="green")
    partner_monster_table.add_column("Level", style="yellow")
    partner_monster_table.add_column("Rarity", style="magenta")

    for monster in partner_monsters:
        partner_monster_table.add_row(
            str(monster.id),
            monster.nickname,
            monster.species.name,
            str(monster.level),
            monster.species.rarity
        )
    console.print(partner_monster_table)
    
    their_monster_id = IntPrompt.ask(f"\nSelect a monster from {trading_partner.username} to receive (enter ID)", 
                                    choices=[str(m.id) for m in partner_monsters])
    their_monster = get_player_monster_by_id(their_monster_id)
    console.print("\n[bold]Trade Summary:[/bold]")
    console.print(f"You will give: [cyan]{your_monster.nickname}[/cyan] ({your_monster.species.name}, {your_monster.species.rarity}, Lvl {your_monster.level})")
    console.print(f"You will receive: [green]{their_monster.nickname}[/green] ({their_monster.species.name}, {their_monster.species.rarity}, Lvl {their_monster.level})")

    
    confirm = Prompt.ask("\nConfirm this trade?", choices=["y", "n"], default="n")
    if confirm.lower() != 'y':
        console.print("[yellow]Trade cancelled.[/yellow]")
        return
    
    try:
        your_monster.player_id = trading_partner.id
        their_monster.player_id = current_player.id
        your_monster.nickname = f"{your_monster.nickname} (from {current_player.username})"
        their_monster.nickname = f"{their_monster.nickname} (from {trading_partner.username})"
        
        session.commit()
        
        console.print(Panel(f"[bold green]Trade completed successfully![/bold green]\n"
                          f"You received [green]{their_monster.nickname}[/green]\n"
                          f"{trading_partner.username} received [cyan]{your_monster.nickname}[/cyan]",
                          border_style="green"))
    except Exception as e:
        session.rollback()
        console.print(f"[red]Error during trade: {str(e)}[/red]")

from time import sleep

def healing_animation(monster_name: str = "your monster"):
    """
    🎥 Visual Healing Animation

    - Displays a live progress bar using Rich's `Live`.
    - Makes healing feel more interactive.
    """
    frames = [
        f"[bold cyan]🌿 {monster_name} lies in the center of the healing circle...[/bold cyan]",
        "[green]🌟 The monster’s wounds begin to close. Light flows into its body... 🌟[/green]",
        "[bold green]✅ Fully healed! It opens its eyes, stronger than ever.[/bold green]"
    ]

    table = Table.grid()
    table.add_column(justify="center", width=70)

    with Live(table, refresh_per_second=6) as live:
        for frame in frames:
            table.columns[0]._cells.clear()
            table.add_row(frame)
            live.update(table)
            sleep(1.0)

def get_max_hp(monster):
    """
    🧮 Get Max HP of Monster

    - Formula: base_hp + (level * 5)
    - Used to validate healing.
    """

    return monster.species.base_hp + (monster.level * 5)  


def heal_monster(session, player):
    """
    💖 Heal Injured Monsters

    - Allows player to heal one or all monsters.
    - Charges coins based on choice.
    - Uses animated progress bars via Rich Live.
    - Updates monsters’ current HP.
    """

    from rich.progress import track
    import time

    SINGLE_HEAL_COST = 10
    BUNDLE_COST_PER_MONSTER = 7 

    if not player.monsters:
        console.print("[bold red]You have no monsters to heal.[/bold red]")
        return

    console.print("\n[bold cyan]🌿 Welcome to the Healing Shrine 🌿[/bold cyan]")
    console.print("[italic]The spirits offer you restoration... but not without tribute.[/italic]\n")

    injured = [m for m in player.monsters if m.current_hp < get_max_hp(m)]

    if not injured:
        time.sleep(1.5)
        console.print("[bold green]Your monsters are already at full health. The spirits give you a high five.[/bold green]\n")
        return

    console.print("[bold]Choose your healing option:[/bold]")
    console.print(f"[1] Heal a single monster — [yellow]{SINGLE_HEAL_COST} coins[/yellow]")
    console.print(f"[2] Heal all injured monsters ({len(injured)} total) — [yellow]{BUNDLE_COST_PER_MONSTER * len(injured)} coins[/yellow]")
    console.print("[0] Cancel and walk away")

    option = IntPrompt.ask("\nYour choice", default=0)

    if option == 0:
        console.print("[italic]You respectfully bow and leave the shrine in peace.[/italic]\n")
        return

    elif option == 1:
        for idx, monster in enumerate(injured, 1):
            max_hp = get_max_hp(monster)
            console.print(
                 f"[{idx}] [bold yellow]{monster.nickname}[/bold yellow] the {monster.species.name} "
                 f"— HP: [red]{monster.current_hp}[/red]/[green]{max_hp}[/green]"
)

        choice = IntPrompt.ask("\nEnter the number of the monster you'd like to heal", default=0)
        if choice < 1 or choice > len(injured):
            console.print("[bold red]Invalid choice. Even the spirits look confused.[/bold red]")
            return

        monster = injured[choice - 1]

        if player.money < SINGLE_HEAL_COST:
            console.print(
                f"[bold red]You need {SINGLE_HEAL_COST} coins. You only have {player.money}.[/bold red]\n"
                "[italic]A ghostly vendor shrugs in disappointment.[/italic]"
            )
            return

        player.money -= SINGLE_HEAL_COST
        prev_hp = monster.current_hp
        monster.current_hp = get_max_hp(monster)
        session.commit()

        console.print("\n✨ [cyan]Mystic light floods the chamber...[/cyan] ✨")
        healing_animation(monster.nickname)


        console.print(
            f"[bold green]{monster.nickname} is fully healed![/bold green] "
            f"[dim]({prev_hp} → {monster.current_hp} HP)[/dim]"
        )
        console.print(f"[bold yellow]-{SINGLE_HEAL_COST} coins[/bold yellow] [dim](Remaining: {player.money})[/dim]\n")

    elif option == 2:
        if len(injured) == 1:
            total_cost = SINGLE_HEAL_COST
        else:
            total_cost = BUNDLE_COST_PER_MONSTER * len(injured)

        if player.money < total_cost:
            console.print(
                f"[bold red]You need {total_cost} coins to heal your monsters, but you only have {player.money}.[/bold red]"
            )
            return

        player.money -= total_cost
        console.print("\n✨ [cyan]The shrine pulses with warm energy...[/cyan] ✨")

        for monster in injured:
            monster.current_hp = get_max_hp(monster)


        session.commit()

        for _ in track(range(30), description="Healing your party..."):
            time.sleep(0.3)

        console.print(f"[bold green]All injured monsters have been fully healed![/bold green]")
        console.print(f"[bold yellow]-{total_cost} coins[/bold yellow] [dim](Remaining: {player.money})[/dim]\n")

        for monster in injured:
            healing_animation(monster.nickname)


 
def main_menu():
    global current_player  
    while True:
        console.rule(f"[bold blue]Main Menu[/bold blue] | Logged in as: [green]{current_player.username}[/green]")
        console.print("[1] View My Profile")
        console.print("[2] View My Monster Collection")
        console.print("[3] Explore and Catch Monsters")
        console.print("[4] Battle a Wild Monster (PvE)")
        console.print("[5] Trade with Players")
        console.print("[6] Logout and Switch Player")
        console.print("[7] Heal Your Monsters")
        console.print("[8] Exit Game")
        
        choice = Prompt.ask("What would you like to do?", choices=["1", "2", "3", "4", "5", "6", "7", "8"])

        if choice == '1':
            view_profile()
        elif choice == '2':
            view_collection()
        elif choice == '3':
            attempt_catch()
        elif choice == '4':
            start_battle()
        elif choice == '5':
            trade_system()
        elif choice == '6':
            current_player = None
            console.print("\n[bold yellow]You have been logged out.[/bold yellow]")
            login_or_register()
        elif choice == '7':
            heal_monster(session, current_player)
        elif choice == '8':
            console.print(Panel("[bold magenta]Thanks for playing Monster World![/bold magenta]"))
            break
        
        if choice in ['1', '2', '3', '4', '5']:
            Prompt.ask("\n[italic]Press Enter to return to the menu...[/italic]")

if __name__ == '__main__':
    print_welcome()
    login_or_register()
    if current_player:
        main_menu()
    
    session.close()