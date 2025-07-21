from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uuid

from .models.game_models import (
    GameResponse, ActionType, Card, GameState, 
    StrategyOverlay, PlayerAction, ActionRequest
)
from .game.poker_engine import PokerEngine
from .game.bot_logic import PokerBot
from .strategies.strategy_engine import StrategyEngine
from .utils.action_generator import ActionGenerator

app = FastAPI(title="Quantitative Finance Poker Training API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory game sessions (in production, use Redis or database)
game_sessions: Dict[str, Dict[str, Any]] = {}

# Initialize engines
poker_engine = PokerEngine()
strategy_engine = StrategyEngine()
poker_bot = PokerBot()

@app.post("/api/game/new", response_model=GameResponse)
async def start_new_game():
    """Start a new poker game session"""
    
    session_id = str(uuid.uuid4())
    
    # Initialize new game
    game_state = poker_engine.deal_new_hand()
    game_state.session_id = session_id
    
    # Store bot cards separately (hidden from user)
    bot_cards = poker_engine.bot_cards
    
    # Store session
    game_sessions[session_id] = {
        "poker_engine": poker_engine,
        "bot_cards": bot_cards,
        "hand_count": 1
    }
    
    # Generate available actions
    available_actions = ActionGenerator.get_available_actions(game_state)
    
    # Generate strategy overlay if it's user's turn
    strategy_overlay = None
    if game_state.active_player == "user":
        try:
            strategy_overlay = strategy_engine.calculate_all_strategies(
                player_cards=game_state.user_cards,
                community_cards=game_state.community_cards,
                pot_size=game_state.pot_size,
                to_call=game_state.to_call,
                player_stack=game_state.user_stack,
                action_history=game_state.action_history,
                street=game_state.street
            )
        except Exception as e:
            print(f"Error calculating strategies: {e}")
    
    return GameResponse(
        game_state=game_state,
        available_actions=available_actions,
        strategy_overlay=strategy_overlay,
        message="New hand dealt! You are in the Big Blind."
    )

@app.post("/api/game/{session_id}/action", response_model=GameResponse)
async def make_action(session_id: str, action_request: ActionRequest):
    """Make a player action"""
    
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = game_sessions[session_id]
    poker_engine = session["poker_engine"]
    bot_cards = session["bot_cards"]
    
    try:
        print(f"DEBUG: Received action - type: {action_request.action_type}, amount: {action_request.amount}")
        
        # Process user action
        amount = action_request.amount or 0
        game_state = poker_engine.process_action(action_request.action_type, amount, "user")
        game_state.session_id = session_id
        
        message = f"You {action_request.action_type.value}"
        if amount > 0:
            message += f" ${amount}"
        
        # Check if hand is over
        if game_state.is_hand_over:
            # Reveal bot cards when hand is over
            game_state.bot_cards = bot_cards
            
            if game_state.winner == "user":
                message += f". You win ${game_state.pot_size}!"
            elif game_state.winner == "bot":
                message += f". Bot wins ${game_state.pot_size}."
            else:
                message += f". Split pot ${game_state.pot_size // 2} each."
            
            return GameResponse(
                game_state=game_state,
                available_actions=[],
                strategy_overlay=None,
                message=message
            )
        
        # If it's bot's turn, make bot move
        if game_state.active_player == "bot":
            bot_action, bot_amount = poker_bot.decide_action(game_state, bot_cards)
            
            # Get bot decision explanation
            equity = poker_engine.get_hand_equity(bot_cards, game_state.community_cards)
            bot_explanation = poker_bot.get_decision_explanation(
                bot_action, bot_amount, equity, game_state.pot_size, game_state.to_call
            )
            
            # Process bot action
            game_state = poker_engine.process_action(bot_action, bot_amount, "bot")
            game_state.session_id = session_id
            
            message += f". {bot_explanation}"
            
            # Check if hand is over after bot action
            if game_state.is_hand_over:
                if game_state.winner == "user":
                    message += f" You win ${game_state.pot_size}!"
                elif game_state.winner == "bot":
                    message += f" Bot wins ${game_state.pot_size}."
                else:
                    message += f" Split pot ${game_state.pot_size // 2} each."
                
                return GameResponse(
                    game_state=game_state,
                    available_actions=[],
                    strategy_overlay=None,
                    message=message
                )
        
        # Generate available actions for user
        available_actions = ActionGenerator.get_available_actions(game_state)
        
        # Generate strategy overlay if it's user's turn
        strategy_overlay = None
        if game_state.active_player == "user":
            try:
                strategy_overlay = strategy_engine.calculate_all_strategies(
                    player_cards=game_state.user_cards,
                    community_cards=game_state.community_cards,
                    pot_size=game_state.pot_size,
                    to_call=game_state.to_call,
                    player_stack=game_state.user_stack,
                    action_history=game_state.action_history,
                    street=game_state.street
                )
            except Exception as e:
                print(f"Error calculating strategies: {e}")
        
        return GameResponse(
            game_state=game_state,
            available_actions=available_actions,
            strategy_overlay=strategy_overlay,
            message=message
        )
        
    except Exception as e:
        print(f"ERROR: Exception in make_action: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Error processing action: {str(e)}")

@app.post("/api/game/{session_id}/next-hand", response_model=GameResponse)
async def deal_next_hand(session_id: str):
    """Deal the next hand in the session"""
    
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = game_sessions[session_id]
    poker_engine = session["poker_engine"]
    
    try:
        # Deal new hand
        game_state = poker_engine.deal_new_hand()
        game_state.session_id = session_id
        
        # Update bot cards
        session["bot_cards"] = poker_engine.bot_cards
        session["hand_count"] += 1
        
        # Generate available actions
        available_actions = ActionGenerator.get_available_actions(game_state)
        
        # Generate strategy overlay
        strategy_overlay = None
        if game_state.active_player == "user":
            try:
                strategy_overlay = strategy_engine.calculate_all_strategies(
                    player_cards=game_state.user_cards,
                    community_cards=game_state.community_cards,
                    pot_size=game_state.pot_size,
                    to_call=game_state.to_call,
                    player_stack=game_state.user_stack,
                    action_history=game_state.action_history,
                    street=game_state.street
                )
            except Exception as e:
                print(f"Error calculating strategies: {e}")
        
        return GameResponse(
            game_state=game_state,
            available_actions=available_actions,
            strategy_overlay=strategy_overlay,
            message=f"Hand #{session['hand_count']} dealt!"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error dealing new hand: {str(e)}")

@app.get("/api/game/{session_id}/status", response_model=GameResponse)
async def get_game_status(session_id: str):
    """Get current game status"""
    
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = game_sessions[session_id]
    poker_engine = session["poker_engine"]
    
    # Get current game state
    game_state = poker_engine._get_game_state(poker_engine._get_next_active_player())
    game_state.session_id = session_id
    
    # Generate available actions
    available_actions = ActionGenerator.get_available_actions(game_state)
    
    # Generate strategy overlay if it's user's turn
    strategy_overlay = None
    if game_state.active_player == "user":
        try:
            strategy_overlay = strategy_engine.calculate_all_strategies(
                player_cards=game_state.user_cards,
                community_cards=game_state.community_cards,
                pot_size=game_state.pot_size,
                to_call=game_state.to_call,
                player_stack=game_state.user_stack,
                action_history=game_state.action_history,
                street=game_state.street
            )
        except Exception as e:
            print(f"Error calculating strategies: {e}")
    
    return GameResponse(
        game_state=game_state,
        available_actions=available_actions,
        strategy_overlay=strategy_overlay,
        message="Current game status"
    )

@app.delete("/api/game/{session_id}")
async def end_game(session_id: str):
    """End a game session"""
    
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    del game_sessions[session_id]
    return {"message": "Game session ended"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Quantitative Finance Poker API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 