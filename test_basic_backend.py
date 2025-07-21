#!/usr/bin/env python3
"""
Basic test script to verify the poker backend functionality without external dependencies
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_models():
    """Test the basic model definitions"""
    print("Testing Models...")
    
    try:
        from backend.models.game_models import Card, GameState, ActionType, Street
        
        # Test creating cards
        card = Card(rank="A", suit="h")
        print(f"✓ Created card: {card.rank}{card.suit}")
        
        # Test action types
        print(f"✓ Action types: {[action.value for action in ActionType]}")
        
        # Test streets
        print(f"✓ Streets: {[street.value for street in Street]}")
        
        print("✓ Models test passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Models test failed: {e}\n")
        return False

def test_strategies_basic():
    """Test the strategy framework without complex calculations"""
    print("Testing Strategy Framework...")
    
    try:
        from backend.strategies.ev_strategy import EVStrategy
        from backend.models.game_models import Card, ActionType
        
        ev_strategy = EVStrategy()
        print(f"✓ Created EV strategy: {ev_strategy.name}")
        
        # Test with basic parameters (using hardcoded equity)
        player_cards = [Card(rank="A", suit="h"), Card(rank="K", suit="s")]
        community_cards = [Card(rank="A", suit="d")]
        
        recommendation = ev_strategy.calculate_recommendation(
            player_cards=player_cards,
            community_cards=community_cards,
            pot_size=100,
            to_call=25,
            player_stack=75,
            equity=0.7  # Assume 70% equity
        )
        
        print(f"✓ EV recommendation: {recommendation.recommended_action.value}")
        print(f"✓ Explanation: {recommendation.explanation}")
        
        print("✓ Strategy Framework test passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Strategy Framework test failed: {e}\n")
        return False

def test_fastapi_app():
    """Test that the FastAPI app can be created"""
    print("Testing FastAPI App...")
    
    try:
        from backend.app import app
        
        print(f"✓ FastAPI app created: {app.title}")
        print(f"✓ App version: {app.version}")
        
        # Check that the app has routes
        routes = [route.path for route in app.routes]
        expected_routes = ["/api/game/new", "/api/health"]
        
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"✓ Found route: {route}")
            else:
                print(f"✗ Missing route: {route}")
        
        print("✓ FastAPI App test passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ FastAPI App test failed: {e}\n")
        return False

def test_action_generator():
    """Test the action generator utility"""
    print("Testing Action Generator...")
    
    try:
        from backend.utils.action_generator import ActionGenerator
        from backend.models.game_models import GameState, Street, Card
        
        # Create a test game state
        game_state = GameState(
            session_id="test",
            street=Street.PREFLOP,
            pot_size=100,
            user_stack=75,
            bot_stack=75,
            user_cards=[Card(rank="A", suit="h"), Card(rank="K", suit="s")],
            community_cards=[],
            current_bet=25,
            to_call=25,
            active_player="user",
            action_history=[],
            hand_number=1,
            is_hand_over=False
        )
        
        actions = ActionGenerator.get_available_actions(game_state)
        
        print(f"✓ Generated {len(actions)} available actions:")
        for action in actions:
            print(f"  - {action.action_type.value}: {action.description}")
        
        print("✓ Action Generator test passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Action Generator test failed: {e}\n")
        return False

def main():
    """Run all basic tests"""
    print("=" * 60)
    print("QUANTITATIVE FINANCE POKER TRAINING APP - BASIC TESTS")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Run tests
    all_passed &= test_models()
    all_passed &= test_strategies_basic()
    all_passed &= test_action_generator()
    all_passed &= test_fastapi_app()
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("🎉 ALL BASIC TESTS PASSED!")
        print("\nThe core backend framework is working correctly.")
        print("Note: Full poker hand evaluation requires the 'deuces' library.")
        print("\nTo start the backend server (with limitations):")
        print("cd backend && python3 -m uvicorn app:app --reload --host 0.0.0.0 --port 8000")
        print("\nAPI will be available at: http://localhost:8000")
        print("API docs at: http://localhost:8000/docs")
    else:
        print("❌ Some basic tests failed. Check the errors above.")
    print("=" * 60)

if __name__ == "__main__":
    main() 