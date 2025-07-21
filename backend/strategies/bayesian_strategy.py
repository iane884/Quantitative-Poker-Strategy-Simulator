from typing import List, Dict, Any
from ..models.game_models import Card, ActionType, StrategyRecommendation, PlayerAction, Street

class BayesianStrategy:
    def __init__(self):
        self.name = "Bayesian Updating"
        # Prior probabilities for opponent hand strength
        self.prior_strong = 0.25  # 25% chance opponent has strong hand initially
        self.prior_medium = 0.50  # 50% chance opponent has medium hand
        self.prior_weak = 0.25    # 25% chance opponent has weak hand
    
    def calculate_recommendation(self, 
                               player_cards: List[Card], 
                               community_cards: List[Card],
                               pot_size: int, 
                               to_call: int, 
                               player_stack: int,
                               action_history: List[PlayerAction],
                               street: Street) -> StrategyRecommendation:
        """
        Apply Bayesian updating based on opponent's actions to estimate their hand strength
        """
        
        # Update beliefs based on opponent's actions
        posterior_probs = self._update_beliefs(action_history, street)
        
        prob_strong = posterior_probs["strong"]
        prob_medium = posterior_probs["medium"] 
        prob_weak = posterior_probs["weak"]
        
        # Make decision based on updated probabilities
        if prob_strong > 0.6:
            # Opponent likely has strong hand
            if to_call > 0:
                # Check if we have strong hand too
                our_strength = self._estimate_our_hand_strength(player_cards, community_cards)
                if our_strength > 0.8:
                    recommended_action = ActionType.CALL
                    decision_reason = "Opponent likely strong, but we have very strong hand"
                else:
                    recommended_action = ActionType.FOLD
                    decision_reason = "Opponent likely has strong hand - fold"
            else:
                recommended_action = ActionType.CHECK
                decision_reason = "Opponent likely strong - check and control pot"
                
        elif prob_weak > 0.5:
            # Opponent likely has weak hand
            if to_call > 0:
                recommended_action = ActionType.RAISE
                recommended_amount = min(pot_size, player_stack)
                decision_reason = "Opponent likely weak - raise for value/fold equity"
            else:
                recommended_action = ActionType.BET
                recommended_amount = min(pot_size // 2, player_stack)
                decision_reason = "Opponent likely weak - bet for value"
                
        else:
            # Uncertain about opponent strength
            if to_call > 0:
                pot_odds = pot_size / (pot_size + to_call) if (pot_size + to_call) > 0 else 0
                our_strength = self._estimate_our_hand_strength(player_cards, community_cards)
                if our_strength > pot_odds + 0.1:  # Need some margin
                    recommended_action = ActionType.CALL
                    decision_reason = "Uncertain opponent strength - call with decent hand"
                else:
                    recommended_action = ActionType.FOLD
                    decision_reason = "Uncertain opponent strength - fold marginal hand"
            else:
                recommended_action = ActionType.CHECK
                decision_reason = "Uncertain opponent strength - check and gather info"
        
        # Build calculation steps showing Bayesian updating
        calculation_steps = self._build_calculation_steps(action_history, posterior_probs)
        
        explanation = f"Bayesian analysis estimates opponent has strong hand {prob_strong:.1%}, medium hand {prob_medium:.1%}, weak hand {prob_weak:.1%}. {decision_reason}."
        
        variables = {
            "prior_strong": f"{self.prior_strong:.1%}",
            "prior_medium": f"{self.prior_medium:.1%}",
            "prior_weak": f"{self.prior_weak:.1%}",
            "posterior_strong": f"{prob_strong:.1%}",
            "posterior_medium": f"{prob_medium:.1%}",
            "posterior_weak": f"{prob_weak:.1%}",
            "most_likely": self._get_most_likely_hand_type(posterior_probs)
        }
        
        confidence = max(prob_strong, prob_medium, prob_weak)
        
        return StrategyRecommendation(
            strategy_name=self.name,
            recommended_action=recommended_action,
            recommended_amount=getattr(locals(), 'recommended_amount', None),
            explanation=explanation,
            formula="P(Hand|Actions) = P(Actions|Hand) × P(Hand) / P(Actions)",
            variables=variables,
            calculation_steps=calculation_steps,
            confidence=confidence
        )
    
    def _update_beliefs(self, action_history: List[PlayerAction], street: Street) -> Dict[str, float]:
        """Update beliefs about opponent hand strength using Bayes' theorem"""
        # Start with priors
        prob_strong = self.prior_strong
        prob_medium = self.prior_medium
        prob_weak = self.prior_weak
        
        # Get only opponent actions
        opponent_actions = [action for action in action_history if action.player == "bot"]
        
        # Update beliefs based on each opponent action
        for action in opponent_actions:
            # Get likelihoods P(Action|Hand_Strength)
            likelihoods = self._get_action_likelihoods(action, street)
            
            # Apply Bayes' theorem
            # P(H|A) = P(A|H) * P(H) / P(A)
            # where P(A) = sum of P(A|H_i) * P(H_i) for all hypotheses
            
            numerator_strong = likelihoods["strong"] * prob_strong
            numerator_medium = likelihoods["medium"] * prob_medium  
            numerator_weak = likelihoods["weak"] * prob_weak
            
            normalizer = numerator_strong + numerator_medium + numerator_weak
            
            if normalizer > 0:
                prob_strong = numerator_strong / normalizer
                prob_medium = numerator_medium / normalizer
                prob_weak = numerator_weak / normalizer
        
        return {
            "strong": prob_strong,
            "medium": prob_medium,
            "weak": prob_weak
        }
    
    def _get_action_likelihoods(self, action: PlayerAction, street: Street) -> Dict[str, float]:
        """Get P(Action|Hand_Strength) for different hand strengths"""
        action_type = action.action_type
        
        # Base likelihoods - how likely each action is given hand strength
        if action_type == ActionType.FOLD:
            return {"strong": 0.05, "medium": 0.30, "weak": 0.70}
        elif action_type == ActionType.CHECK:
            return {"strong": 0.20, "medium": 0.60, "weak": 0.40}
        elif action_type == ActionType.CALL:
            return {"strong": 0.60, "medium": 0.50, "weak": 0.20}
        elif action_type in [ActionType.BET, ActionType.RAISE]:
            # Adjust based on bet size relative to pot
            if action.amount > 0:
                # Large bets more likely with strong hands
                if action.amount > 50:  # Large bet
                    return {"strong": 0.80, "medium": 0.30, "weak": 0.15}
                else:  # Small bet
                    return {"strong": 0.60, "medium": 0.40, "weak": 0.25}
            else:
                # Default bet
                return {"strong": 0.70, "medium": 0.35, "weak": 0.20}
        else:
            # Default neutral likelihoods
            return {"strong": 0.33, "medium": 0.33, "weak": 0.33}
    
    def _estimate_our_hand_strength(self, player_cards: List[Card], community_cards: List[Card]) -> float:
        """Estimate strength of our own hand (0-1 scale)"""
        # Simple heuristic based on card ranks and pairs
        ranks = [card.rank for card in player_cards]
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                      '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        values = [rank_values.get(rank, 0) for rank in ranks]
        
        # Pocket pair bonus
        if values[0] == values[1]:
            base_strength = 0.5 + (max(values) / 28)  # Pair strength
        else:
            # High card strength
            base_strength = (max(values) + min(values)) / 28
            
            # Suited bonus
            if len(set(card.suit for card in player_cards)) == 1:
                base_strength += 0.05
        
        # Adjust based on community cards (simplified)
        if len(community_cards) > 0:
            # Check for potential improvements
            community_ranks = [card.rank for card in community_cards]
            
            # Simple check for pairs with board
            for card in player_cards:
                if card.rank in community_ranks:
                    base_strength += 0.2  # Made a pair
                    break
        
        return min(1.0, base_strength)
    
    def _build_calculation_steps(self, action_history: List[PlayerAction], 
                               posterior_probs: Dict[str, float]) -> List[str]:
        """Build step-by-step calculation showing Bayesian updating"""
        steps = [
            f"Starting priors: Strong={self.prior_strong:.1%}, Medium={self.prior_medium:.1%}, Weak={self.prior_weak:.1%}"
        ]
        
        opponent_actions = [action for action in action_history if action.player == "bot"]
        
        if not opponent_actions:
            steps.append("No opponent actions to analyze - using priors")
        else:
            steps.append("Updating beliefs based on opponent actions:")
            
            for i, action in enumerate(opponent_actions):
                likelihoods = self._get_action_likelihoods(action, Street.PREFLOP)  # Simplified
                steps.append(f"Action {i+1}: {action.action_type}")
                steps.append(f"  P({action.action_type}|Strong)={likelihoods['strong']:.2f}")
                steps.append(f"  P({action.action_type}|Medium)={likelihoods['medium']:.2f}")
                steps.append(f"  P({action.action_type}|Weak)={likelihoods['weak']:.2f}")
        
        steps.extend([
            f"Final posteriors: Strong={posterior_probs['strong']:.1%}, Medium={posterior_probs['medium']:.1%}, Weak={posterior_probs['weak']:.1%}",
            f"Most likely: {self._get_most_likely_hand_type(posterior_probs)}"
        ])
        
        return steps
    
    def _get_most_likely_hand_type(self, probs: Dict[str, float]) -> str:
        """Get the most likely hand type"""
        return max(probs.items(), key=lambda x: x[1])[0] 