from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class ActionType(str, Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"

class Street(str, Enum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"

class Card(BaseModel):
    rank: str  # '2'-'9', 'T', 'J', 'Q', 'K', 'A'
    suit: str  # 'h', 'd', 'c', 's'

class PlayerAction(BaseModel):
    action_type: ActionType
    amount: int = 0
    player: str  # "user" or "bot"

class ActionRequest(BaseModel):
    action_type: ActionType
    amount: Optional[int] = 0

class GameState(BaseModel):
    session_id: str
    street: Street
    pot_size: int
    user_stack: int
    bot_stack: int
    user_cards: List[Card]
    bot_cards: Optional[List[Card]] = None  # Only shown when hand is over
    community_cards: List[Card]
    current_bet: int
    to_call: int
    active_player: str  # "user" or "bot"
    action_history: List[PlayerAction]
    hand_number: int
    is_hand_over: bool
    winner: Optional[str] = None
    showdown_result: Optional[Dict[str, Any]] = None

class AvailableAction(BaseModel):
    action_type: ActionType
    amount: Optional[int] = None
    description: str

class StrategyRecommendation(BaseModel):
    strategy_name: str
    recommended_action: ActionType
    recommended_amount: Optional[int] = None
    explanation: str
    formula: str
    variables: Dict[str, Any]
    calculation_steps: List[str]
    confidence: float  # 0.0 to 1.0

class StrategyOverlay(BaseModel):
    ev_strategy: StrategyRecommendation
    monte_carlo_strategy: StrategyRecommendation
    bayesian_strategy: StrategyRecommendation
    kelly_strategy: StrategyRecommendation
    risk_utility_strategy: StrategyRecommendation
    gto_strategy: StrategyRecommendation

class GameResponse(BaseModel):
    game_state: GameState
    available_actions: List[AvailableAction]
    strategy_overlay: Optional[StrategyOverlay] = None
    message: str 