#!/usr/bin/env python3
"""
Simple test script to verify the poker backend functionality
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_poker_engine():
    """Test the poker engine functionality"""
    print("Testing Poker Engine...")
    
    try:
        from backend.game.poker_engine import PokerEngine
        from backend.models.game_models import ActionType
        
        engine = PokerEngine()
        
        # Test dealing a new hand
        print("✓ Dealing new hand...")
        game_state = engine.deal_new_hand()
        print(f"  User cards: {[f'{c.rank}{c.suit}' for c in game_state.user_cards]}")
        print(f"  Pot size: ${game_state.pot_size}")
        print(f"  User stack: ${game_state.user_stack}")
        print(f"  Active player: {game_state.active_player}")
        
        # Test processing an action
        print("✓ Processing user action (call)...")
        new_state = engine.process_action(ActionType.CALL, 0, "user")
        print(f"  New pot size: ${new_state.pot_size}")
        print(f"  New active player: {new_state.active_player}")
        
        print("✓ Poker Engine test passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Poker Engine test failed: {e}\n")
        return False

def test_strategies():
    """Test the strategy calculations"""
    print("Testing Strategy Engine...")
    
    try:
        from backend.strategies.strategy_engine import StrategyEngine
        from backend.models.game_models import Card, Street, PlayerAction
        
        strategy_engine = StrategyEngine()
        
        # Create test data
        player_cards = [
            Card(rank="A", suit="h"),
            Card(rank="K", suit="s")
        ]
        community_cards = [
            Card(rank="A", suit="d"),
            Card(rank="Q", suit="c"),
            Card(rank="J", suit="h")
        ]
        
        print("✓ Calculating all strategies...")
        print(f"  Player cards: Ah Ks")
        print(f"  Board: Ad Qc Jh")
        
        strategy_overlay = strategy_engine.calculate_all_strategies(
            player_cards=player_cards,
            community_cards=community_cards,
            pot_size=100,
            to_call=25,
            player_stack=75,
            action_history=[],
            street=Street.FLOP
        )
        
        print(f"  EV Strategy: {strategy_overlay.ev_strategy.recommended_action.value}")
        print(f"  Monte Carlo: {strategy_overlay.monte_carlo_strategy.recommended_action.value}")
        print(f"  Bayesian: {strategy_overlay.bayesian_strategy.recommended_action.value}")
        print(f"  Kelly: {strategy_overlay.kelly_strategy.recommended_action.value}")
        print(f"  Risk Utility: {strategy_overlay.risk_utility_strategy.recommended_action.value}")
        print(f"  GTO: {strategy_overlay.gto_strategy.recommended_action.value}")
        
        print("✓ Strategy Engine test passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Strategy Engine test failed: {e}\n")
        return False

def test_bot_logic():
    """Test the bot decision making"""
    print("Testing Bot Logic...")
    
    try:
        from backend.game.bot_logic import PokerBot
        from backend.models.game_models import Card, GameState, Street
        
        bot = PokerBot()
        
        # Create test game state
        bot_cards = [
            Card(rank="Q", suit="h"),
            Card(rank="Q", suit="s")
        ]
        
        game_state = GameState(
            session_id="test",
            street=Street.FLOP,
            pot_size=50,
            user_stack=75,
            bot_stack=75,
            user_cards=[],  # Bot doesn't see user cards
            community_cards=[
                Card(rank="A", suit="d"),
                Card(rank="Q", suit="c"),
                Card(rank="J", suit="h")
            ],
            current_bet=0,
            to_call=25,
            active_player="bot",
            action_history=[],
            hand_number=1,
            is_hand_over=False
        )
        
        print("✓ Bot making decision...")
        print(f"  Bot cards: Qh Qs (pocket queens)")
        print(f"  Board: Ad Qc Jh")
        print(f"  To call: $25")
        
        action, amount = bot.decide_action(game_state, bot_cards)
        explanation = bot.get_decision_explanation(action, amount, 0.85, 50, 25)
        
        print(f"  Bot decision: {action.value} ${amount if amount > 0 else ''}")
        print(f"  Explanation: {explanation}")
        
        print("✓ Bot Logic test passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Bot Logic test failed: {e}\n")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("QUANTITATIVE FINANCE POKER TRAINING APP - BACKEND TESTS")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Run tests
    all_passed &= test_poker_engine()
    all_passed &= test_strategies()
    all_passed &= test_bot_logic()
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Backend is ready to run.")
        print("\nTo start the backend server:")
        print("cd backend && python main.py")
        print("\nAPI will be available at: http://localhost:8000")
        print("API docs at: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Check the errors above.")
    print("=" * 60)

if __name__ == "__main__":
    main() 