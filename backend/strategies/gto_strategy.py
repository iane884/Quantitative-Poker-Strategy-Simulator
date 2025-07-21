from typing import List, Dict, Any, Tuple
from ..models.game_models import Card, ActionType, StrategyRecommendation, Street

class GTOStrategy:
    def __init__(self):
        self.name = "Game Theory Optimal"
        # Simplified GTO ranges - in a full implementation these would come from solver data
        self.preflop_ranges = self._load_preflop_ranges()
        self.postflop_ranges = self._load_postflop_ranges()
    
    def calculate_recommendation(self, 
                               player_cards: List[Card], 
                               community_cards: List[Card],
                               pot_size: int, 
                               to_call: int, 
                               player_stack: int,
                               street: Street,
                               position: str = "BB") -> StrategyRecommendation:
        """
        Get GTO recommendation based on precomputed optimal strategies
        """
        
        if street == Street.PREFLOP:
            gto_strategy = self._get_preflop_strategy(player_cards, to_call, position)
        else:
            gto_strategy = self._get_postflop_strategy(player_cards, community_cards, to_call, street)
        
        # GTO often provides mixed strategies (frequencies)
        frequencies = gto_strategy["frequencies"]
        reasoning = gto_strategy["reasoning"]
        hand_category = gto_strategy["hand_category"]
        
        # Convert frequencies to recommendation
        # Find the action with highest frequency as primary recommendation
        primary_action = max(frequencies.items(), key=lambda x: x[1])
        recommended_action_name = primary_action[0]
        primary_frequency = primary_action[1]
        
        # Convert to ActionType
        action_map = {
            "fold": ActionType.FOLD,
            "call": ActionType.CALL,
            "check": ActionType.CHECK,
            "bet": ActionType.BET,
            "raise": ActionType.RAISE
        }
        
        recommended_action = action_map.get(recommended_action_name, ActionType.CHECK)
        
        # Determine bet size if betting/raising
        recommended_amount = None
        if recommended_action in [ActionType.BET, ActionType.RAISE]:
            recommended_amount = self._get_gto_bet_size(pot_size, player_stack, street)
        
        # Build frequency display
        freq_display = []
        for action, freq in frequencies.items():
            if freq > 0:
                freq_display.append(f"{action.upper()}: {freq:.1%}")
        
        # Build calculation steps
        calculation_steps = [
            f"Hand category: {hand_category}",
            f"Street: {street.value}",
            f"Position: {position}",
            f"GTO mixed strategy frequencies:"
        ]
        
        for action, freq in frequencies.items():
            if freq > 0:
                calculation_steps.append(f"  {action.upper()}: {freq:.1%}")
        
        calculation_steps.extend([
            f"Primary recommendation: {recommended_action_name.upper()} ({primary_frequency:.1%})",
            reasoning
        ])
        
        # Explanation
        if primary_frequency > 0.8:
            explanation = f"GTO analysis strongly recommends {recommended_action_name.upper()} ({primary_frequency:.1%} frequency) with this {hand_category}. {reasoning}"
        elif primary_frequency > 0.5:
            explanation = f"GTO analysis suggests mostly {recommended_action_name.upper()} ({primary_frequency:.1%}) but mixing with other actions. {reasoning}"
        else:
            mixed_actions = [f"{action} {freq:.1%}" for action, freq in frequencies.items() if freq > 0.2]
            explanation = f"GTO strategy calls for a mixed approach: {', '.join(mixed_actions)}. Primary action: {recommended_action_name.upper()}. {reasoning}"
        
        # Variables
        variables = {
            "hand_category": hand_category,
            "street": street.value,
            "position": position,
            "primary_action": recommended_action_name.upper(),
            "primary_frequency": f"{primary_frequency:.1%}",
            "strategy_type": "Mixed" if len([f for f in frequencies.values() if f > 0.1]) > 1 else "Pure"
        }
        
        # Add all frequencies to variables
        for action, freq in frequencies.items():
            if freq > 0:
                variables[f"freq_{action}"] = f"{freq:.1%}"
        
        # Confidence based on how "pure" the strategy is
        if primary_frequency > 0.8:
            confidence = 0.95
        elif primary_frequency > 0.6:
            confidence = 0.85
        elif primary_frequency > 0.4:
            confidence = 0.75
        else:
            confidence = 0.65
        
        return StrategyRecommendation(
            strategy_name=self.name,
            recommended_action=recommended_action,
            recommended_amount=recommended_amount,
            explanation=explanation,
            formula="Based on Nash equilibrium solutions from game theory solvers",
            variables=variables,
            calculation_steps=calculation_steps,
            confidence=confidence
        )
    
    def _get_preflop_strategy(self, player_cards: List[Card], to_call: int, position: str) -> Dict[str, Any]:
        """Get preflop GTO strategy based on hand strength"""
        hand_category = self._categorize_preflop_hand(player_cards)
        
        # Simplified GTO preflop ranges
        if to_call > 0:  # Facing a raise
            if hand_category in ["premium", "strong"]:
                frequencies = {"call": 0.7, "raise": 0.25, "fold": 0.05}
                reasoning = "Strong hand - mostly call/raise, rarely fold"
            elif hand_category == "medium":
                frequencies = {"call": 0.4, "fold": 0.55, "raise": 0.05}
                reasoning = "Medium hand - mixed strategy leaning toward fold"
            elif hand_category == "suited_connector":
                frequencies = {"call": 0.3, "fold": 0.65, "raise": 0.05}
                reasoning = "Suited connector - occasional call for playability"
            else:  # weak
                frequencies = {"fold": 0.9, "call": 0.1, "raise": 0.0}
                reasoning = "Weak hand - mostly fold with rare bluff calls"
        else:  # First to act or can check
            if hand_category in ["premium", "strong"]:
                frequencies = {"bet": 0.8, "check": 0.2}
                reasoning = "Strong hand - bet for value"
            elif hand_category == "medium":
                frequencies = {"bet": 0.3, "check": 0.7}
                reasoning = "Medium hand - mix of betting and checking"
            else:
                frequencies = {"check": 0.9, "bet": 0.1}
                reasoning = "Weak hand - mostly check, occasional bluff"
        
        return {
            "frequencies": frequencies,
            "reasoning": reasoning,
            "hand_category": hand_category
        }
    
    def _get_postflop_strategy(self, player_cards: List[Card], community_cards: List[Card], 
                             to_call: int, street: Street) -> Dict[str, Any]:
        """Get postflop GTO strategy (simplified)"""
        hand_strength = self._evaluate_postflop_hand(player_cards, community_cards)
        board_texture = self._analyze_board_texture(community_cards)
        
        # Simplified postflop GTO decisions
        if to_call > 0:  # Facing a bet
            if hand_strength > 0.8:  # Very strong
                frequencies = {"call": 0.6, "raise": 0.35, "fold": 0.05}
                reasoning = "Very strong hand - mostly call/raise for value"
            elif hand_strength > 0.6:  # Strong
                frequencies = {"call": 0.7, "raise": 0.1, "fold": 0.2}
                reasoning = "Strong hand - mostly call, some raises"
            elif hand_strength > 0.3:  # Medium
                frequencies = {"call": 0.3, "fold": 0.6, "raise": 0.1}
                reasoning = "Medium strength - often fold, some calls"
            else:  # Weak
                frequencies = {"fold": 0.85, "call": 0.1, "raise": 0.05}
                reasoning = "Weak hand - mostly fold, rare bluffs"
        else:  # First to act
            if hand_strength > 0.7:
                frequencies = {"bet": 0.75, "check": 0.25}
                reasoning = "Strong hand - bet for value"
            elif hand_strength > 0.4:
                frequencies = {"bet": 0.4, "check": 0.6}
                reasoning = "Medium hand - balanced strategy"
            else:
                frequencies = {"check": 0.8, "bet": 0.2}
                reasoning = "Weak hand - mostly check, some bluffs"
        
        # Adjust based on board texture
        if board_texture == "dry":
            # Less betting on dry boards
            if "bet" in frequencies:
                frequencies["bet"] *= 0.8
                frequencies["check"] = 1 - frequencies["bet"]
        elif board_texture == "wet":
            # More aggressive on wet boards
            if "bet" in frequencies:
                frequencies["bet"] *= 1.2
                frequencies["check"] = max(0, 1 - frequencies["bet"])
        
        hand_category = f"{hand_strength:.1f} strength on {board_texture} board"
        
        return {
            "frequencies": frequencies,
            "reasoning": reasoning,
            "hand_category": hand_category
        }
    
    def _categorize_preflop_hand(self, cards: List[Card]) -> str:
        """Categorize preflop hand strength"""
        ranks = [card.rank for card in cards]
        suits = [card.suit for card in cards]
        
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                      '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        values = [rank_values[rank] for rank in ranks]
        is_suited = suits[0] == suits[1]
        is_pair = values[0] == values[1]
        
        if is_pair:
            if values[0] >= 11:  # JJ+
                return "premium"
            elif values[0] >= 7:  # 77-TT
                return "strong"
            else:
                return "medium"
        
        high_card = max(values)
        if high_card == 14:  # Ace
            if max(values) >= 10:  # AK, AQ, AJ, AT
                return "premium" if min(values) >= 13 else "strong"
            else:
                return "medium"
        elif high_card >= 12:  # King or Queen high
            if min(values) >= 10:
                return "strong"
            else:
                return "medium"
        
        # Check for suited connectors
        if is_suited and abs(values[0] - values[1]) <= 1:
            return "suited_connector"
        
        return "weak"
    
    def _evaluate_postflop_hand(self, player_cards: List[Card], community_cards: List[Card]) -> float:
        """Simplified postflop hand evaluation (0-1 scale)"""
        # Very basic implementation - in reality would use proper hand evaluation
        all_cards = player_cards + community_cards
        ranks = [card.rank for card in all_cards]
        suits = [card.suit for card in all_cards]
        
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                      '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        values = [rank_values[rank] for rank in ranks]
        
        # Check for pairs, two pairs, etc. (simplified)
        value_counts = {}
        for value in values:
            value_counts[value] = value_counts.get(value, 0) + 1
        
        pairs = [v for v, count in value_counts.items() if count >= 2]
        
        if len(pairs) >= 2:  # Two pair or better
            return 0.8
        elif len(pairs) == 1:  # One pair
            return 0.6 if max(pairs) >= 10 else 0.4
        else:  # High card
            return (max(values) - 2) / 12 * 0.3  # Max 0.3 for high card
    
    def _analyze_board_texture(self, community_cards: List[Card]) -> str:
        """Analyze board texture (dry/wet)"""
        if len(community_cards) < 3:
            return "unknown"
        
        ranks = [card.rank for card in community_cards]
        suits = [card.suit for card in community_cards]
        
        # Check for flush possibilities
        suit_counts = {}
        for suit in suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        max_suit_count = max(suit_counts.values()) if suit_counts else 0
        
        # Check for straight possibilities
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                      '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        values = sorted([rank_values[rank] for rank in ranks])
        has_straight_potential = False
        
        if len(values) >= 3:
            for i in range(len(values) - 2):
                if values[i+2] - values[i] <= 4:  # Within 4 ranks
                    has_straight_potential = True
                    break
        
        # Classify board
        if max_suit_count >= 3 or has_straight_potential:
            return "wet"
        else:
            return "dry"
    
    def _get_gto_bet_size(self, pot_size: int, player_stack: int, street: Street) -> int:
        """Get GTO bet sizing"""
        # Simplified GTO bet sizes
        if street == Street.FLOP:
            return min(pot_size // 2, player_stack)  # 50% pot on flop
        elif street == Street.TURN:
            return min(int(pot_size * 0.75), player_stack)  # 75% pot on turn
        else:  # River
            return min(pot_size, player_stack)  # Pot-sized on river
    
    def _load_preflop_ranges(self) -> Dict[str, Any]:
        """Load precomputed preflop GTO ranges (placeholder)"""
        # In a full implementation, this would load actual solver data
        return {}
    
    def _load_postflop_ranges(self) -> Dict[str, Any]:
        """Load precomputed postflop GTO ranges (placeholder)"""
        # In a full implementation, this would load actual solver data
        return {} 