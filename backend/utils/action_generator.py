from typing import List
from ..models.game_models import AvailableAction, ActionType, GameState

class ActionGenerator:
    @staticmethod
    def get_available_actions(game_state: GameState) -> List[AvailableAction]:
        """Generate list of available actions for the user"""
        
        actions = []
        
        if game_state.to_call > 0:
            # Facing a bet
            
            # Always can fold
            actions.append(AvailableAction(
                action_type=ActionType.FOLD,
                amount=None,
                description="Fold and forfeit the hand"
            ))
            
            # Can call if we have enough chips
            if game_state.user_stack >= game_state.to_call:
                actions.append(AvailableAction(
                    action_type=ActionType.CALL,
                    amount=game_state.to_call,
                    description=f"Call ${game_state.to_call}"
                ))
            
            # Can raise if we have enough chips for a meaningful raise
            min_raise = game_state.to_call + max(game_state.current_bet, 1)
            if game_state.user_stack >= min_raise:
                # Offer a few raise sizes
                
                # Minimum raise
                actions.append(AvailableAction(
                    action_type=ActionType.RAISE,
                    amount=min(min_raise, game_state.user_stack),
                    description=f"Minimum raise to ${min_raise}"
                ))
                
                # Pot-sized raise
                pot_raise = game_state.to_call + game_state.pot_size
                if game_state.user_stack >= pot_raise and pot_raise > min_raise:
                    actions.append(AvailableAction(
                        action_type=ActionType.RAISE,
                        amount=min(pot_raise, game_state.user_stack),
                        description=f"Pot raise to ${pot_raise}"
                    ))
                
                # All-in (if different from above)
                if game_state.user_stack > pot_raise:
                    actions.append(AvailableAction(
                        action_type=ActionType.ALL_IN,
                        amount=game_state.user_stack,
                        description=f"All-in ${game_state.user_stack}"
                    ))
        
        else:
            # First to act (no bet to call)
            
            # Always can check
            actions.append(AvailableAction(
                action_type=ActionType.CHECK,
                amount=None,
                description="Check (no bet)"
            ))
            
            # Can bet if we have chips
            if game_state.user_stack > 0:
                # Small bet (1/3 pot)
                small_bet = max(1, game_state.pot_size // 3)
                if game_state.user_stack >= small_bet:
                    actions.append(AvailableAction(
                        action_type=ActionType.BET,
                        amount=min(small_bet, game_state.user_stack),
                        description=f"Small bet ${small_bet} (1/3 pot)"
                    ))
                
                # Half pot bet
                half_pot = max(1, game_state.pot_size // 2)
                if game_state.user_stack >= half_pot and half_pot > small_bet:
                    actions.append(AvailableAction(
                        action_type=ActionType.BET,
                        amount=min(half_pot, game_state.user_stack),
                        description=f"Half pot ${half_pot}"
                    ))
                
                # Pot-sized bet
                pot_bet = max(1, game_state.pot_size)
                if game_state.user_stack >= pot_bet and pot_bet > half_pot:
                    actions.append(AvailableAction(
                        action_type=ActionType.BET,
                        amount=min(pot_bet, game_state.user_stack),
                        description=f"Pot bet ${pot_bet}"
                    ))
                
                # All-in (if significantly different)
                if game_state.user_stack > pot_bet * 1.5:
                    actions.append(AvailableAction(
                        action_type=ActionType.ALL_IN,
                        amount=game_state.user_stack,
                        description=f"All-in ${game_state.user_stack}"
                    ))
        
        return actions 