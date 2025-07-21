import math
from typing import List, Dict, Any
from ..models.game_models import Card, ActionType, StrategyRecommendation

class RiskUtilityStrategy:
    def __init__(self, risk_aversion_lambda: float = 0.5):
        self.name = "Risk-Adjusted Utility"
        self.lambda_risk = risk_aversion_lambda  # Risk aversion coefficient
    
    def calculate_recommendation(self, 
                               player_cards: List[Card], 
                               community_cards: List[Card],
                               pot_size: int, 
                               to_call: int, 
                               player_stack: int,
                               equity: float) -> StrategyRecommendation:
        """
        Calculate risk-adjusted utility for different actions
        
        Utility = Expected Value - λ × Variance
        where λ is the risk aversion parameter
        """
        
        p_win = equity
        p_lose = 1 - p_win
        
        # Calculate utility for different actions
        utilities = {}
        
        # Utility of folding (always 0 EV and 0 variance)
        utilities["fold"] = {
            "ev": 0.0,
            "variance": 0.0,
            "utility": 0.0
        }
        
        if to_call > 0:
            # Utility of calling
            win_amount = pot_size + to_call
            lose_amount = to_call
            
            ev_call = p_win * win_amount - p_lose * lose_amount
            variance_call = p_win * (win_amount - ev_call) ** 2 + p_lose * (-lose_amount - ev_call) ** 2
            utility_call = ev_call - self.lambda_risk * variance_call
            
            utilities["call"] = {
                "ev": ev_call,
                "variance": variance_call,
                "utility": utility_call
            }
        else:
            # Utility of checking (pot equity with no risk)
            ev_check = p_win * pot_size
            variance_check = p_win * (pot_size - ev_check) ** 2 + p_lose * (0 - ev_check) ** 2
            utility_check = ev_check - self.lambda_risk * variance_check
            
            utilities["check"] = {
                "ev": ev_check,
                "variance": variance_check,
                "utility": utility_check
            }
        
        # Utility of betting/raising
        bet_size = min(pot_size, player_stack)
        fold_prob = self._estimate_fold_probability(equity, bet_size, pot_size)
        call_prob = 1 - fold_prob
        
        # Expected outcomes when betting
        # Scenario 1: Opponent folds (probability = fold_prob)
        fold_outcome = pot_size
        
        # Scenario 2: Opponent calls (probability = call_prob)
        if call_prob > 0:
            call_win_outcome = pot_size + bet_size
            call_lose_outcome = -bet_size
            
            # Combined EV when opponent calls
            call_scenario_ev = p_win * call_win_outcome + p_lose * call_lose_outcome
        else:
            call_scenario_ev = 0
        
        # Overall EV of betting
        ev_bet = fold_prob * fold_outcome + call_prob * call_scenario_ev
        
        # Variance calculation for betting
        # This is more complex due to multiple scenarios
        variance_bet = (
            fold_prob * (fold_outcome - ev_bet) ** 2 +
            call_prob * p_win * (call_win_outcome - ev_bet) ** 2 +
            call_prob * p_lose * (call_lose_outcome - ev_bet) ** 2
        )
        
        utility_bet = ev_bet - self.lambda_risk * variance_bet
        
        utilities["bet"] = {
            "ev": ev_bet,
            "variance": variance_bet,
            "utility": utility_bet
        }
        
        # Find action with highest utility
        best_action = max(utilities.items(), key=lambda x: x[1]["utility"])
        best_action_name = best_action[0]
        best_utility_data = best_action[1]
        
        # Convert to ActionType
        action_map = {
            "fold": ActionType.FOLD,
            "call": ActionType.CALL,
            "check": ActionType.CHECK,
            "bet": ActionType.BET,
            "raise": ActionType.RAISE
        }
        
        if best_action_name == "bet" and to_call > 0:
            recommended_action = ActionType.RAISE
        else:
            recommended_action = action_map[best_action_name]
        
        recommended_amount = bet_size if best_action_name in ["bet", "raise"] else None
        
        # Build calculation steps
        calculation_steps = [
            f"Risk-Adjusted Utility Formula: U = EV - λ × Variance",
            f"Risk aversion parameter (λ) = {self.lambda_risk}",
            f"Win probability = {p_win:.3f}",
            f"Lose probability = {p_lose:.3f}"
        ]
        
        # Add calculations for each action
        for action_name, data in utilities.items():
            if action_name == "call" and to_call == 0:
                continue
            if action_name == "check" and to_call > 0:
                continue
                
            calculation_steps.extend([
                f"{action_name.upper()}:",
                f"  EV = ${data['ev']:.2f}",
                f"  Variance = ${data['variance']:.2f}",
                f"  Utility = ${data['ev']:.2f} - {self.lambda_risk} × ${data['variance']:.2f} = ${data['utility']:.2f}"
            ])
        
        calculation_steps.append(f"Best action: {best_action_name.upper()} (Utility = ${best_utility_data['utility']:.2f})")
        
        # Risk assessment
        best_variance = best_utility_data['variance']
        if best_variance > 100:
            risk_level = "High"
        elif best_variance > 25:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Explanation
        if best_utility_data['utility'] > 0:
            explanation = f"Risk-adjusted analysis recommends {best_action_name.upper()} with utility of ${best_utility_data['utility']:.2f}. Risk level: {risk_level}. The strategy accounts for both expected value (${best_utility_data['ev']:.2f}) and risk (variance: ${best_variance:.2f})."
        else:
            explanation = f"Risk-adjusted analysis suggests {best_action_name.upper()} as the least risky option, though utility is negative (${best_utility_data['utility']:.2f}). All available actions have negative risk-adjusted value."
        
        # Variables
        variables = {
            "risk_aversion_lambda": str(self.lambda_risk),
            "win_probability": f"{p_win:.3f}",
            "best_action": best_action_name.upper(),
            "best_ev": f"${best_utility_data['ev']:.2f}",
            "best_variance": f"${best_utility_data['variance']:.2f}",
            "best_utility": f"${best_utility_data['utility']:.2f}",
            "risk_level": risk_level
        }
        
        # Add specific action utilities
        for action_name, data in utilities.items():
            if action_name in ["call", "check", "bet", "fold"]:
                variables[f"{action_name}_utility"] = f"${data['utility']:.2f}"
        
        # Confidence based on utility difference and risk level
        utility_values = [data['utility'] for data in utilities.values()]
        utility_range = max(utility_values) - min(utility_values)
        
        if utility_range > 20:  # Clear utility difference
            confidence = 0.9
        elif utility_range > 10:
            confidence = 0.8
        elif utility_range > 5:
            confidence = 0.7
        else:
            confidence = 0.6
        
        # Adjust confidence based on risk level
        if risk_level == "High":
            confidence *= 0.9  # Slightly less confident in high-risk situations
        
        return StrategyRecommendation(
            strategy_name=self.name,
            recommended_action=recommended_action,
            recommended_amount=recommended_amount,
            explanation=explanation,
            formula="Utility = Expected Value - λ × Variance (λ = risk aversion parameter)",
            variables=variables,
            calculation_steps=calculation_steps,
            confidence=confidence
        )
    
    def _estimate_fold_probability(self, equity: float, bet_size: int, pot_size: int) -> float:
        """Estimate opponent fold probability for variance calculations"""
        bet_to_pot_ratio = bet_size / pot_size if pot_size > 0 else 1.0
        
        # Base fold rate
        if bet_to_pot_ratio <= 0.5:
            base_fold_rate = 0.3
        elif bet_to_pot_ratio <= 1.0:
            base_fold_rate = 0.5
        else:
            base_fold_rate = 0.7
        
        # Adjust based on hand strength
        if equity > 0.8:
            base_fold_rate += 0.1
        elif equity < 0.3:
            base_fold_rate -= 0.1
        
        return max(0.1, min(0.9, base_fold_rate)) 