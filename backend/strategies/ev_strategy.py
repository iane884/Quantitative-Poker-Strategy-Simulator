from typing import List, Dict, Any
from ..models.game_models import Card, ActionType, StrategyRecommendation

class EVStrategy:
    def __init__(self):
        self.name = "Expected Value"
    
    def calculate_recommendation(self, 
                               player_cards: List[Card], 
                               community_cards: List[Card],
                               pot_size: int, 
                               to_call: int, 
                               player_stack: int,
                               equity: float) -> StrategyRecommendation:
        """
        Calculate Expected Value recommendation
        
        EV(Call) = P_win * (pot + bet) - P_lose * (bet)
        EV(Fold) = 0
        EV(Bet) = P_opponent_folds * pot + P_opponent_calls * [P_win * (pot + bet) - P_lose * bet]
        """
        
        # Calculate EV for different actions
        p_win = equity
        p_lose = 1 - p_win
        
        # EV of folding is always 0
        ev_fold = 0.0
        
        # EV of calling (if there's a bet to call)
        ev_call = 0.0
        if to_call > 0:
            ev_call = p_win * (pot_size + to_call) - p_lose * to_call
        
        # EV of checking (if no bet to call)
        ev_check = p_win * pot_size if to_call == 0 else 0
        
        # EV of betting/raising (simplified: assume pot-sized bet)
        bet_size = min(pot_size, player_stack)
        p_opponent_folds = self._estimate_fold_probability(equity, bet_size, pot_size)
        p_opponent_calls = 1 - p_opponent_folds
        
        ev_bet = (p_opponent_folds * pot_size + 
                  p_opponent_calls * (p_win * (pot_size + bet_size) - p_lose * bet_size))
        
        # Determine best action
        actions_ev = []
        
        if to_call > 0:
            actions_ev.extend([
                ("fold", ev_fold),
                ("call", ev_call),
                ("raise", ev_bet)
            ])
        else:
            actions_ev.extend([
                ("check", ev_check),
                ("bet", ev_bet)
            ])
        
        # Find action with highest EV
        best_action, best_ev = max(actions_ev, key=lambda x: x[1])
        
        # Convert to ActionType
        action_map = {
            "fold": ActionType.FOLD,
            "call": ActionType.CALL,
            "check": ActionType.CHECK,
            "bet": ActionType.BET,
            "raise": ActionType.RAISE
        }
        
        recommended_action = action_map[best_action]
        recommended_amount = bet_size if best_action in ["bet", "raise"] else None
        
        # Build calculation steps
        calculation_steps = [
            f"P_win (equity) = {p_win:.3f}",
            f"P_lose = {p_lose:.3f}",
            f"Pot size = ${pot_size}"
        ]
        
        if to_call > 0:
            calculation_steps.extend([
                f"Amount to call = ${to_call}",
                f"EV(Fold) = $0.00",
                f"EV(Call) = {p_win:.3f} × ${pot_size + to_call} - {p_lose:.3f} × ${to_call} = ${ev_call:.2f}",
                f"EV(Raise) = {p_opponent_folds:.3f} × ${pot_size} + {p_opponent_calls:.3f} × [{p_win:.3f} × ${pot_size + bet_size} - {p_lose:.3f} × ${bet_size}] = ${ev_bet:.2f}"
            ])
        else:
            calculation_steps.extend([
                f"EV(Check) = {p_win:.3f} × ${pot_size} = ${ev_check:.2f}",
                f"EV(Bet ${bet_size}) = {p_opponent_folds:.3f} × ${pot_size} + {p_opponent_calls:.3f} × [{p_win:.3f} × ${pot_size + bet_size} - {p_lose:.3f} × ${bet_size}] = ${ev_bet:.2f}"
            ])
        
        calculation_steps.append(f"Best action: {best_action.upper()} (EV = ${best_ev:.2f})")
        
        # Build explanation
        if best_ev > 0:
            explanation = f"EV analysis suggests {best_action.upper()} with positive expected value of ${best_ev:.2f}. This decision is profitable in the long run."
        else:
            explanation = f"EV analysis suggests {best_action.upper()}. While EV is ${best_ev:.2f}, this is the least negative option available."
        
        variables = {
            "equity": f"{p_win:.3f}",
            "pot_size": f"${pot_size}",
            "to_call": f"${to_call}" if to_call > 0 else "No bet",
            "ev_fold": f"${ev_fold:.2f}",
            "ev_call": f"${ev_call:.2f}" if to_call > 0 else "N/A",
            "ev_check": f"${ev_check:.2f}" if to_call == 0 else "N/A",
            "ev_bet": f"${ev_bet:.2f}",
            "best_ev": f"${best_ev:.2f}"
        }
        
        return StrategyRecommendation(
            strategy_name=self.name,
            recommended_action=recommended_action,
            recommended_amount=recommended_amount,
            explanation=explanation,
            formula="EV(action) = P_win × (amount_won) - P_lose × (amount_risked)",
            variables=variables,
            calculation_steps=calculation_steps,
            confidence=0.9 if abs(best_ev) > 5 else 0.7  # Higher confidence for clear +/- EV spots
        )
    
    def _estimate_fold_probability(self, equity: float, bet_size: int, pot_size: int) -> float:
        """Estimate opponent fold probability based on bet sizing and board texture"""
        # Simplified model: higher bets and worse boards lead to more folds
        bet_to_pot_ratio = bet_size / pot_size if pot_size > 0 else 1.0
        
        # Base fold rate based on bet sizing
        if bet_to_pot_ratio <= 0.5:
            base_fold_rate = 0.3
        elif bet_to_pot_ratio <= 1.0:
            base_fold_rate = 0.5
        else:
            base_fold_rate = 0.7
        
        # Adjust based on our perceived hand strength
        # If we have a strong hand, opponent might fold more often
        if equity > 0.8:
            base_fold_rate += 0.1
        elif equity < 0.3:
            base_fold_rate -= 0.1
        
        return max(0.1, min(0.9, base_fold_rate)) 