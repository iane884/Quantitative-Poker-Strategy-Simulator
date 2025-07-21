from typing import List, Dict, Any
from ..models.game_models import Card, ActionType, StrategyRecommendation

class KellyStrategy:
    def __init__(self):
        self.name = "Kelly Criterion"
    
    def calculate_recommendation(self, 
                               player_cards: List[Card], 
                               community_cards: List[Card],
                               pot_size: int, 
                               to_call: int, 
                               player_stack: int,
                               equity: float) -> StrategyRecommendation:
        """
        Apply Kelly Criterion for optimal bet sizing
        
        Kelly Formula: f* = (bp - q) / b
        where:
        - f* = fraction of bankroll to bet
        - b = odds received on the bet (pot size / bet size)
        - p = probability of winning
        - q = probability of losing (1 - p)
        """
        
        p_win = equity
        p_lose = 1 - p_win
        
        # Calculate Kelly fraction for different scenarios
        kelly_results = {}
        
        if to_call > 0:
            # Calling scenario
            pot_odds = pot_size / to_call if to_call > 0 else 0  # Odds we're getting
            b = pot_odds  # The "b" in Kelly formula
            
            kelly_fraction = (b * p_win - p_lose) / b if b > 0 else 0
            kelly_amount = kelly_fraction * player_stack
            
            kelly_results["call"] = {
                "fraction": kelly_fraction,
                "amount": kelly_amount,
                "odds": b
            }
        
        # Betting scenario (assume pot-sized bet)
        bet_size = min(pot_size, player_stack)
        if bet_size > 0:
            pot_odds_if_bet = pot_size / bet_size  # Odds if we bet
            b_bet = pot_odds_if_bet
            
            # Need to account for opponent folding probability
            fold_prob = self._estimate_fold_probability(equity, bet_size, pot_size)
            
            # Adjusted Kelly considering fold equity
            # EV = fold_prob * pot + (1-fold_prob) * [p_win * (pot + bet) - p_lose * bet]
            # Simplified Kelly for betting: weight by fold equity
            
            kelly_fraction_bet = (b_bet * p_win - p_lose) / b_bet if b_bet > 0 else 0
            kelly_fraction_bet = max(0, kelly_fraction_bet)  # Can't be negative
            
            # Adjust for fold equity
            kelly_fraction_bet *= (1 + fold_prob)  # Bonus for fold equity
            
            kelly_amount_bet = kelly_fraction_bet * player_stack
            
            kelly_results["bet"] = {
                "fraction": kelly_fraction_bet,
                "amount": kelly_amount_bet,
                "odds": b_bet
            }
        
        # Determine recommendation based on Kelly fractions
        if to_call > 0:
            call_kelly = kelly_results.get("call", {})
            call_fraction = call_kelly.get("fraction", 0)
            call_amount = call_kelly.get("amount", 0)
            
            if call_fraction > 0 and to_call <= call_amount:
                # Kelly supports calling
                recommended_action = ActionType.CALL
                recommended_amount = None
                decision_reason = f"Kelly supports calling (optimal fraction: {call_fraction:.1%})"
                
                # Check if we should raise instead
                bet_kelly = kelly_results.get("bet", {})
                bet_fraction = bet_kelly.get("fraction", 0)
                
                if bet_fraction > call_fraction * 1.5:  # Significantly higher Kelly for betting
                    recommended_action = ActionType.RAISE
                    optimal_bet = min(bet_kelly.get("amount", bet_size), player_stack)
                    recommended_amount = max(to_call + pot_size // 2, optimal_bet)
                    decision_reason = f"Kelly strongly favors raising (optimal fraction: {bet_fraction:.1%})"
            else:
                # Kelly doesn't support calling
                recommended_action = ActionType.FOLD
                recommended_amount = None
                decision_reason = f"Kelly advises against calling (negative or insufficient edge)"
        else:
            # No bet to call - decide between check and bet
            bet_kelly = kelly_results.get("bet", {})
            bet_fraction = bet_kelly.get("fraction", 0)
            
            if bet_fraction > 0.05:  # At least 5% of stack justified
                recommended_action = ActionType.BET
                recommended_amount = min(bet_kelly.get("amount", bet_size), player_stack)
                decision_reason = f"Kelly supports betting {bet_fraction:.1%} of stack"
            else:
                recommended_action = ActionType.CHECK
                recommended_amount = None
                decision_reason = "Kelly doesn't justify betting (insufficient edge)"
        
        # Build calculation steps
        calculation_steps = [
            f"Kelly Formula: f* = (bp - q) / b",
            f"p (win probability) = {p_win:.3f}",
            f"q (lose probability) = {p_lose:.3f}",
            f"Current stack = ${player_stack}"
        ]
        
        if to_call > 0:
            call_kelly = kelly_results.get("call", {})
            calculation_steps.extend([
                f"Calling scenario:",
                f"  Pot odds (b) = ${pot_size} / ${to_call} = {call_kelly.get('odds', 0):.2f}",
                f"  Kelly fraction = ({call_kelly.get('odds', 0):.2f} × {p_win:.3f} - {p_lose:.3f}) / {call_kelly.get('odds', 0):.2f} = {call_kelly.get('fraction', 0):.3f}",
                f"  Optimal amount = {call_kelly.get('fraction', 0):.3f} × ${player_stack} = ${call_kelly.get('amount', 0):.0f}",
                f"  Required call = ${to_call}"
            ])
        
        if "bet" in kelly_results:
            bet_kelly = kelly_results["bet"]
            calculation_steps.extend([
                f"Betting scenario:",
                f"  Bet size = ${bet_size}",
                f"  Pot odds if bet = ${pot_size} / ${bet_size} = {bet_kelly.get('odds', 0):.2f}",
                f"  Kelly fraction = {bet_kelly.get('fraction', 0):.3f}",
                f"  Optimal bet amount = ${bet_kelly.get('amount', 0):.0f}"
            ])
        
        calculation_steps.append(f"Recommendation: {decision_reason}")
        
        # Explanation
        if hasattr(locals(), 'call_fraction') and call_fraction > 0:
            explanation = f"Kelly Criterion suggests optimal betting fraction of {max(kelly_results.get('call', {}).get('fraction', 0), kelly_results.get('bet', {}).get('fraction', 0)):.1%} of your stack. {decision_reason}."
        else:
            explanation = f"Kelly Criterion analysis: {decision_reason}."
        
        # Variables
        variables = {
            "win_probability": f"{p_win:.3f}",
            "lose_probability": f"{p_lose:.3f}",
            "player_stack": f"${player_stack}",
            "pot_size": f"${pot_size}",
            "to_call": f"${to_call}" if to_call > 0 else "No bet"
        }
        
        # Add Kelly-specific variables
        if to_call > 0 and "call" in kelly_results:
            variables.update({
                "pot_odds": f"{kelly_results['call']['odds']:.2f}",
                "kelly_fraction_call": f"{kelly_results['call']['fraction']:.3f}",
                "optimal_call_amount": f"${kelly_results['call']['amount']:.0f}"
            })
        
        if "bet" in kelly_results:
            variables.update({
                "kelly_fraction_bet": f"{kelly_results['bet']['fraction']:.3f}",
                "optimal_bet_amount": f"${kelly_results['bet']['amount']:.0f}"
            })
        
        # Confidence based on clarity of Kelly recommendation
        max_kelly_fraction = max(
            kelly_results.get('call', {}).get('fraction', 0),
            kelly_results.get('bet', {}).get('fraction', 0)
        )
        
        if max_kelly_fraction > 0.2:
            confidence = 0.9
        elif max_kelly_fraction > 0.1:
            confidence = 0.8
        elif max_kelly_fraction > 0.05:
            confidence = 0.7
        else:
            confidence = 0.6
        
        return StrategyRecommendation(
            strategy_name=self.name,
            recommended_action=recommended_action,
            recommended_amount=recommended_amount,
            explanation=explanation,
            formula="f* = (bp - q) / b, where f* = optimal fraction, b = odds, p = win prob, q = lose prob",
            variables=variables,
            calculation_steps=calculation_steps,
            confidence=confidence
        )
    
    def _estimate_fold_probability(self, equity: float, bet_size: int, pot_size: int) -> float:
        """Estimate opponent fold probability for Kelly betting calculations"""
        bet_to_pot_ratio = bet_size / pot_size if pot_size > 0 else 1.0
        
        # Base fold rate
        if bet_to_pot_ratio <= 0.5:
            base_fold_rate = 0.3
        elif bet_to_pot_ratio <= 1.0:
            base_fold_rate = 0.5
        else:
            base_fold_rate = 0.7
        
        # Adjust based on our hand strength
        if equity > 0.8:
            base_fold_rate += 0.1
        elif equity < 0.3:
            base_fold_rate -= 0.1
        
        return max(0.1, min(0.9, base_fold_rate)) 