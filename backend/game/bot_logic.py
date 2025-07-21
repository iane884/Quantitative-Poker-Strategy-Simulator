from typing import List, Tuple
from ..models.game_models import Card, ActionType, GameState
from ..game.poker_engine import PokerEngine

class PokerBot:
    def __init__(self):
        self.name = "EV Bot"
        self.poker_engine = PokerEngine()
    
    def decide_action(self, game_state: GameState, bot_cards: List[Card]) -> Tuple[ActionType, int]:
        """
        Make a decision based on Expected Value calculations
        
        This bot uses a simplified EV-based strategy to provide consistent,
        educational gameplay that demonstrates quantitative decision making.
        """
        
        # Calculate hand equity
        equity = self.poker_engine.get_hand_equity(
            bot_cards, 
            game_state.community_cards
        )
        
        pot_size = game_state.pot_size
        to_call = game_state.to_call
        bot_stack = game_state.bot_stack
        
        # EV-based decision making
        if to_call > 0:
            # Facing a bet - calculate EV of calling vs folding
            ev_call = self._calculate_call_ev(equity, pot_size, to_call)
            ev_fold = 0.0  # Folding always has 0 EV
            
            # Also consider raising
            raise_size = min(pot_size, bot_stack)
            ev_raise = self._calculate_raise_ev(equity, pot_size, to_call, raise_size)
            
            # Choose action with highest EV
            actions = [
                (ActionType.FOLD, ev_fold),
                (ActionType.CALL, ev_call),
                (ActionType.RAISE, ev_raise)
            ]
            
            best_action, best_ev = max(actions, key=lambda x: x[1])
            
            if best_action == ActionType.RAISE:
                return best_action, raise_size
            else:
                return best_action, 0
        
        else:
            # First to act - decide between check and bet
            ev_check = equity * pot_size  # Simplified check EV
            
            bet_size = min(pot_size // 2, bot_stack)  # Conservative bet sizing
            ev_bet = self._calculate_bet_ev(equity, pot_size, bet_size)
            
            if ev_bet > ev_check and ev_bet > 0:
                return ActionType.BET, bet_size
            else:
                return ActionType.CHECK, 0
    
    def _calculate_call_ev(self, equity: float, pot_size: int, to_call: int) -> float:
        """Calculate Expected Value of calling"""
        p_win = equity
        p_lose = 1 - p_win
        
        # EV = P(win) * (pot + bet) - P(lose) * bet
        return p_win * (pot_size + to_call) - p_lose * to_call
    
    def _calculate_raise_ev(self, equity: float, pot_size: int, to_call: int, raise_size: int) -> float:
        """Calculate Expected Value of raising"""
        p_win = equity
        p_lose = 1 - p_win
        
        # Estimate opponent fold probability based on raise size
        fold_prob = self._estimate_opponent_fold_probability(raise_size, pot_size)
        call_prob = 1 - fold_prob
        
        # EV = P(fold) * current_pot + P(call) * [P(win) * (pot + raise) - P(lose) * raise]
        ev_if_fold = pot_size
        ev_if_call = p_win * (pot_size + raise_size) - p_lose * raise_size
        
        return fold_prob * ev_if_fold + call_prob * ev_if_call
    
    def _calculate_bet_ev(self, equity: float, pot_size: int, bet_size: int) -> float:
        """Calculate Expected Value of betting"""
        p_win = equity
        p_lose = 1 - p_win
        
        # Estimate opponent fold probability
        fold_prob = self._estimate_opponent_fold_probability(bet_size, pot_size)
        call_prob = 1 - fold_prob
        
        # EV = P(fold) * pot + P(call) * [P(win) * (pot + bet) - P(lose) * bet]
        ev_if_fold = pot_size
        ev_if_call = p_win * (pot_size + bet_size) - p_lose * bet_size
        
        return fold_prob * ev_if_fold + call_prob * ev_if_call
    
    def _estimate_opponent_fold_probability(self, bet_size: int, pot_size: int) -> float:
        """
        Estimate probability that opponent will fold to our bet
        
        This is a simplified model for educational purposes.
        In reality, this would depend on opponent modeling and history.
        """
        if pot_size == 0:
            return 0.5  # Default
        
        bet_to_pot_ratio = bet_size / pot_size
        
        # Simple model: larger bets get more folds
        if bet_to_pot_ratio <= 0.25:
            base_fold_rate = 0.2
        elif bet_to_pot_ratio <= 0.5:
            base_fold_rate = 0.35
        elif bet_to_pot_ratio <= 1.0:
            base_fold_rate = 0.5
        elif bet_to_pot_ratio <= 2.0:
            base_fold_rate = 0.65
        else:
            base_fold_rate = 0.8
        
        # Add some randomness to make play less predictable
        import random
        randomness = random.uniform(-0.1, 0.1)
        
        return max(0.1, min(0.9, base_fold_rate + randomness))
    
    def get_decision_explanation(self, action: ActionType, amount: int, 
                               equity: float, pot_size: int, to_call: int) -> str:
        """
        Generate an explanation for the bot's decision for educational purposes
        """
        if action == ActionType.FOLD:
            return f"Bot folded: EV of calling was negative with {equity:.1%} equity"
        elif action == ActionType.CALL:
            ev_call = self._calculate_call_ev(equity, pot_size, to_call)
            return f"Bot called: EV = ${ev_call:.2f} with {equity:.1%} equity"
        elif action == ActionType.CHECK:
            return f"Bot checked: Controlling pot size with {equity:.1%} equity"
        elif action == ActionType.BET:
            ev_bet = self._calculate_bet_ev(equity, pot_size, amount)
            return f"Bot bet ${amount}: EV = ${ev_bet:.2f} for value/fold equity"
        elif action == ActionType.RAISE:
            ev_raise = self._calculate_raise_ev(equity, pot_size, to_call, amount)
            return f"Bot raised to ${amount}: EV = ${ev_raise:.2f} with {equity:.1%} equity"
        else:
            return f"Bot chose {action.value}" 