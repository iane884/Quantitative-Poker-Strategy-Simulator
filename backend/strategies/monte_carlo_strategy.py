import random
from typing import List, Dict, Any
from ..models.game_models import Card, ActionType, StrategyRecommendation
from ..game.poker_engine import PokerEngine

class MonteCarloStrategy:
    def __init__(self, num_simulations: int = 1000):
        self.name = "Monte Carlo Simulation"
        self.num_simulations = num_simulations
        self.poker_engine = PokerEngine()
    
    def calculate_recommendation(self, 
                               player_cards: List[Card], 
                               community_cards: List[Card],
                               pot_size: int, 
                               to_call: int, 
                               player_stack: int) -> StrategyRecommendation:
        """
        Run Monte Carlo simulation to estimate win probability and make recommendations
        """
        
        # Run simulations
        simulation_results = self._run_simulations(player_cards, community_cards)
        
        wins = simulation_results["wins"]
        ties = simulation_results["ties"]
        losses = simulation_results["losses"]
        total = wins + ties + losses
        
        win_percentage = (wins / total) * 100 if total > 0 else 50.0
        tie_percentage = (ties / total) * 100 if total > 0 else 0.0
        loss_percentage = (losses / total) * 100 if total > 0 else 50.0
        
        # Use win probability for decision making
        equity = wins / total if total > 0 else 0.5
        
        # Apply simple decision rules based on simulation results
        if win_percentage >= 70:
            if to_call > 0:
                recommended_action = ActionType.RAISE if win_percentage >= 80 else ActionType.CALL
                recommended_amount = min(pot_size, player_stack) if recommended_action == ActionType.RAISE else None
                decision_reason = "Strong favorite - aggressive play recommended"
            else:
                recommended_action = ActionType.BET
                recommended_amount = min(pot_size, player_stack)
                decision_reason = "Strong favorite - bet for value"
        elif win_percentage >= 45:
            if to_call > 0:
                # Check pot odds
                pot_odds = pot_size / (pot_size + to_call) if (pot_size + to_call) > 0 else 0
                if equity > pot_odds:
                    recommended_action = ActionType.CALL
                    recommended_amount = None
                    decision_reason = "Favorable pot odds - call is profitable"
                else:
                    recommended_action = ActionType.FOLD
                    recommended_amount = None
                    decision_reason = "Insufficient pot odds - fold"
            else:
                recommended_action = ActionType.CHECK
                recommended_amount = None
                decision_reason = "Marginal hand - check and see"
        else:
            recommended_action = ActionType.FOLD if to_call > 0 else ActionType.CHECK
            recommended_amount = None
            decision_reason = "Poor win rate - avoid investing more"
        
        # Build calculation steps
        calculation_steps = [
            f"Ran {self.num_simulations} Monte Carlo simulations",
            f"Results: {wins} wins, {ties} ties, {losses} losses",
            f"Win rate: {win_percentage:.1f}%",
            f"Tie rate: {tie_percentage:.1f}%", 
            f"Loss rate: {loss_percentage:.1f}%",
            f"Equity: {equity:.3f}",
            decision_reason
        ]
        
        if to_call > 0:
            pot_odds = pot_size / (pot_size + to_call)
            calculation_steps.append(f"Pot odds: {pot_odds:.3f} ({pot_odds*100:.1f}%)")
            calculation_steps.append(f"Equity vs Pot Odds: {equity:.3f} vs {pot_odds:.3f}")
        
        explanation = f"Monte Carlo simulation of {self.num_simulations} random outcomes shows you win {win_percentage:.1f}% of the time. {decision_reason}."
        
        variables = {
            "simulations": str(self.num_simulations),
            "wins": str(wins),
            "ties": str(ties), 
            "losses": str(losses),
            "win_percentage": f"{win_percentage:.1f}%",
            "equity": f"{equity:.3f}",
            "pot_odds": f"{pot_size / (pot_size + to_call):.3f}" if to_call > 0 else "N/A"
        }
        
        confidence = self._calculate_confidence(win_percentage, total)
        
        return StrategyRecommendation(
            strategy_name=self.name,
            recommended_action=recommended_action,
            recommended_amount=recommended_amount,
            explanation=explanation,
            formula=f"Run {self.num_simulations} random simulations of remaining cards and count wins/losses",
            variables=variables,
            calculation_steps=calculation_steps,
            confidence=confidence
        )
    
    def _run_simulations(self, player_cards: List[Card], community_cards: List[Card]) -> Dict[str, int]:
        """Run Monte Carlo simulations"""
        wins = 0
        ties = 0
        losses = 0
        
        # Get remaining cards
        used_cards = set()
        for card in player_cards + community_cards:
            used_cards.add((card.rank, card.suit))
        
        # Create deck of remaining cards
        remaining_cards = []
        for suit in ['h', 'd', 'c', 's']:
            for rank in ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']:
                if (rank, suit) not in used_cards:
                    remaining_cards.append(Card(rank=rank, suit=suit))
        
        # Run simulations
        for _ in range(self.num_simulations):
            # Shuffle remaining cards
            random.shuffle(remaining_cards)
            
            # Deal opponent cards
            opponent_cards = remaining_cards[:2]
            deck_pos = 2
            
            # Complete the board if needed
            sim_community = community_cards.copy()
            cards_needed = 5 - len(community_cards)
            
            if cards_needed > 0:
                sim_community.extend(remaining_cards[deck_pos:deck_pos + cards_needed])
            
            # Evaluate hands
            result = self._compare_hands(player_cards, opponent_cards, sim_community)
            
            if result == 1:
                wins += 1
            elif result == 0:
                ties += 1
            else:
                losses += 1
        
        return {"wins": wins, "ties": ties, "losses": losses}
    
    def _compare_hands(self, player_cards: List[Card], opponent_cards: List[Card], 
                      community_cards: List[Card]) -> int:
        """Compare two hands. Returns 1 if player wins, 0 for tie, -1 if opponent wins"""
        try:
            # Convert to deuces format
            player_deuces = [self.poker_engine._card_to_deuces(card) for card in player_cards]
            opponent_deuces = [self.poker_engine._card_to_deuces(card) for card in opponent_cards]
            board_deuces = [self.poker_engine._card_to_deuces(card) for card in community_cards]
            
            # Evaluate hands (lower score is better in deuces)
            player_score = self.poker_engine.evaluator.evaluate(board_deuces, player_deuces)
            opponent_score = self.poker_engine.evaluator.evaluate(board_deuces, opponent_deuces)
            
            if player_score < opponent_score:
                return 1  # Player wins
            elif player_score > opponent_score:
                return -1  # Opponent wins
            else:
                return 0  # Tie
        except:
            # Fallback to simple comparison if deuces fails
            return self._simple_hand_compare(player_cards, opponent_cards, community_cards)
    
    def _simple_hand_compare(self, player_cards: List[Card], opponent_cards: List[Card], 
                           community_cards: List[Card]) -> int:
        """Simplified hand comparison fallback"""
        # Very basic comparison - just compare high cards
        player_ranks = [self._rank_value(card.rank) for card in player_cards]
        opponent_ranks = [self._rank_value(card.rank) for card in opponent_cards]
        
        player_high = max(player_ranks)
        opponent_high = max(opponent_ranks)
        
        if player_high > opponent_high:
            return 1
        elif opponent_high > player_high:
            return -1
        else:
            return 0
    
    def _rank_value(self, rank: str) -> int:
        """Convert rank to numeric value"""
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                      '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        return rank_values.get(rank, 0)
    
    def _calculate_confidence(self, win_percentage: float, total_simulations: int) -> float:
        """Calculate confidence based on sample size and result clarity"""
        # Higher confidence for more simulations and more extreme results
        base_confidence = min(0.95, 0.6 + (total_simulations / 2000))
        
        # Adjust based on how clear the result is
        if win_percentage > 80 or win_percentage < 20:
            return min(0.95, base_confidence + 0.2)
        elif win_percentage > 70 or win_percentage < 30:
            return min(0.9, base_confidence + 0.1)
        else:
            return base_confidence 