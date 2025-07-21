from typing import List, Dict, Any
from ..models.game_models import Card, StrategyOverlay, Street, PlayerAction
from .ev_strategy import EVStrategy
from .monte_carlo_strategy import MonteCarloStrategy
from .bayesian_strategy import BayesianStrategy
from .kelly_strategy import KellyStrategy
from .risk_utility_strategy import RiskUtilityStrategy
from .gto_strategy import GTOStrategy
from ..game.poker_engine import PokerEngine

class StrategyEngine:
    def __init__(self):
        self.poker_engine = PokerEngine()
        
        # Initialize all strategy calculators
        self.ev_strategy = EVStrategy()
        self.monte_carlo_strategy = MonteCarloStrategy(num_simulations=1000)
        self.bayesian_strategy = BayesianStrategy()
        self.kelly_strategy = KellyStrategy()
        self.risk_utility_strategy = RiskUtilityStrategy(risk_aversion_lambda=0.5)
        self.gto_strategy = GTOStrategy()
    
    def calculate_all_strategies(self, 
                               player_cards: List[Card],
                               community_cards: List[Card],
                               pot_size: int,
                               to_call: int,
                               player_stack: int,
                               action_history: List[PlayerAction],
                               street: Street) -> StrategyOverlay:
        """
        Calculate recommendations from all 6 quantitative strategies
        """
        
        # Calculate hand equity (needed by multiple strategies)
        equity = self.poker_engine.get_hand_equity(player_cards, community_cards)
        
        try:
            # 1. Expected Value Strategy
            ev_recommendation = self.ev_strategy.calculate_recommendation(
                player_cards=player_cards,
                community_cards=community_cards,
                pot_size=pot_size,
                to_call=to_call,
                player_stack=player_stack,
                equity=equity
            )
        except Exception as e:
            print(f"Error in EV strategy: {e}")
            ev_recommendation = self._create_fallback_recommendation("Expected Value", "Error in calculation")
        
        try:
            # 2. Monte Carlo Simulation Strategy
            monte_carlo_recommendation = self.monte_carlo_strategy.calculate_recommendation(
                player_cards=player_cards,
                community_cards=community_cards,
                pot_size=pot_size,
                to_call=to_call,
                player_stack=player_stack
            )
        except Exception as e:
            print(f"Error in Monte Carlo strategy: {e}")
            monte_carlo_recommendation = self._create_fallback_recommendation("Monte Carlo", "Error in simulation")
        
        try:
            # 3. Bayesian Updating Strategy
            bayesian_recommendation = self.bayesian_strategy.calculate_recommendation(
                player_cards=player_cards,
                community_cards=community_cards,
                pot_size=pot_size,
                to_call=to_call,
                player_stack=player_stack,
                action_history=action_history,
                street=street
            )
        except Exception as e:
            print(f"Error in Bayesian strategy: {e}")
            bayesian_recommendation = self._create_fallback_recommendation("Bayesian", "Error in belief updating")
        
        try:
            # 4. Kelly Criterion Strategy
            kelly_recommendation = self.kelly_strategy.calculate_recommendation(
                player_cards=player_cards,
                community_cards=community_cards,
                pot_size=pot_size,
                to_call=to_call,
                player_stack=player_stack,
                equity=equity
            )
        except Exception as e:
            print(f"Error in Kelly strategy: {e}")
            kelly_recommendation = self._create_fallback_recommendation("Kelly Criterion", "Error in bankroll calculation")
        
        try:
            # 5. Risk-Adjusted Utility Strategy
            risk_utility_recommendation = self.risk_utility_strategy.calculate_recommendation(
                player_cards=player_cards,
                community_cards=community_cards,
                pot_size=pot_size,
                to_call=to_call,
                player_stack=player_stack,
                equity=equity
            )
        except Exception as e:
            print(f"Error in Risk Utility strategy: {e}")
            risk_utility_recommendation = self._create_fallback_recommendation("Risk-Adjusted Utility", "Error in utility calculation")
        
        try:
            # 6. Game Theory Optimal Strategy
            gto_recommendation = self.gto_strategy.calculate_recommendation(
                player_cards=player_cards,
                community_cards=community_cards,
                pot_size=pot_size,
                to_call=to_call,
                player_stack=player_stack,
                street=street,
                position="BB"  # Simplified position for heads-up
            )
        except Exception as e:
            print(f"Error in GTO strategy: {e}")
            gto_recommendation = self._create_fallback_recommendation("GTO", "Error in solver lookup")
        
        return StrategyOverlay(
            ev_strategy=ev_recommendation,
            monte_carlo_strategy=monte_carlo_recommendation,
            bayesian_strategy=bayesian_recommendation,
            kelly_strategy=kelly_recommendation,
            risk_utility_strategy=risk_utility_recommendation,
            gto_strategy=gto_recommendation
        )
    
    def _create_fallback_recommendation(self, strategy_name: str, error_msg: str):
        """Create a fallback recommendation when a strategy fails"""
        from ..models.game_models import StrategyRecommendation, ActionType
        
        return StrategyRecommendation(
            strategy_name=strategy_name,
            recommended_action=ActionType.CHECK,
            recommended_amount=None,
            explanation=f"Error occurred: {error_msg}",
            formula="N/A",
            variables={"error": error_msg},
            calculation_steps=[f"Error: {error_msg}"],
            confidence=0.0
        ) 