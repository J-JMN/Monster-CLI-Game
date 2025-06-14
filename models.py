import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DB_PATH = os.path.join(BASE_DIR, "monster_game.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    money = Column(Integer, default=100)
    created_at = Column(DateTime, server_default=func.now())
    monsters = relationship("PlayerMonster", back_populates="owner", cascade="all, delete-orphan")
    achievements = relationship("PlayerAchievement", back_populates="player", cascade="all, delete-orphan")
    battles_as_player1 = relationship("Battle", foreign_keys="Battle.player1_id", back_populates="player1")
    battles_as_player2 = relationship("Battle", foreign_keys="Battle.player2_id", back_populates="player2")
    battles_won = relationship("Battle", foreign_keys="Battle.winner_id")
    trades_proposed = relationship("Trade", foreign_keys="Trade.proposing_player_id", back_populates="proposing_player")
    trades_accepted = relationship("Trade", foreign_keys="Trade.accepting_player_id", back_populates="accepting_player")

    def __repr__(self):
        return f"<Player(id={self.id}, username='{self.username}', level={self.level})>"

class MonsterSpecies(Base):
    __tablename__ = 'monster_species'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    monster_type = Column(String, nullable=False)
    rarity = Column(String, nullable=False)
    base_hp = Column(Integer, nullable=False)
    base_attack = Column(Integer, nullable=False)
    base_defense = Column(Integer, nullable=False)
    instances = relationship("PlayerMonster", back_populates="species")

    def __repr__(self):
        return f"<MonsterSpecies(id={self.id}, name='{self.name}', type='{self.monster_type}')>"

class PlayerMonster(Base):
    __tablename__ = 'player_monsters'
    id = Column(Integer, primary_key=True)
    nickname = Column(String)
    level = Column(Integer, default=1)
    current_experience = Column(Integer, default=0)
    current_hp = Column(Integer, nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    species_id = Column(Integer, ForeignKey('monster_species.id'), nullable=False)
    owner = relationship("Player", back_populates="monsters")
    species = relationship("MonsterSpecies", back_populates="instances")
    proposed_trades = relationship("Trade", foreign_keys="Trade.proposing_player_monster_id", back_populates="proposing_monster")
    accepted_trades = relationship("Trade", foreign_keys="Trade.accepting_player_monster_id", back_populates="accepting_monster")

    def __repr__(self):
        return f"<PlayerMonster(id={self.id}, nickname='{self.nickname}', level={self.level})>"

class Battle(Base):
    __tablename__ = 'battles'
    id = Column(Integer, primary_key=True)
    battle_timestamp = Column(DateTime, server_default=func.now())
    turns_taken = Column(Integer)
    player1_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    player2_id = Column(Integer, ForeignKey('players.id'))
    winner_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    player1 = relationship("Player", foreign_keys=[player1_id], back_populates="battles_as_player1")
    player2 = relationship("Player", foreign_keys=[player2_id], back_populates="battles_as_player2")
    winner = relationship("Player", foreign_keys=[winner_id], back_populates="battles_won")
class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True)
    status = Column(String, default='proposed')
    trade_timestamp = Column(DateTime, server_default=func.now())
    proposing_player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    accepting_player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    proposing_player_monster_id = Column(Integer, ForeignKey('player_monsters.id'), nullable=False)
    accepting_player_monster_id = Column(Integer, ForeignKey('player_monsters.id'))
    proposing_player = relationship("Player", foreign_keys=[proposing_player_id], back_populates="trades_proposed")
    accepting_player = relationship("Player", foreign_keys=[accepting_player_id], back_populates="trades_accepted")
    proposing_monster = relationship("PlayerMonster", foreign_keys=[proposing_player_monster_id], back_populates="proposed_trades")
    accepting_monster = relationship("PlayerMonster", foreign_keys=[accepting_player_monster_id], back_populates="accepted_trades")

class Achievement(Base):
    __tablename__ = 'achievements'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    
    player_links = relationship("PlayerAchievement", back_populates="achievement")

    def __repr__(self):
        return f"<Achievement(id={self.id}, name='{self.name}')>"

class PlayerAchievement(Base):
    __tablename__ = 'player_achievements'
    player_id = Column(Integer, ForeignKey('players.id'), primary_key=True)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), primary_key=True)
    unlocked_at = Column(DateTime, server_default=func.now())
    player = relationship("Player", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="player_links")

def create_db():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    create_db()
    print("Database and tables created successfully.")