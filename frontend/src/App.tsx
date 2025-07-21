import React, { useState, useCallback } from 'react';
import PokerTable from './components/PokerTable';
import StrategyPanel from './components/StrategyPanel';
import { GameState, StrategyOverlay, AvailableAction } from './types/GameTypes';
import { GameAPI } from './services/GameAPI';
import './App.css';

function App() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [strategyOverlay, setStrategyOverlay] = useState<StrategyOverlay | null>(null);
  const [availableActions, setAvailableActions] = useState<AvailableAction[]>([]);
  const [gameMessage, setGameMessage] = useState<string>('');
  const [sessionId, setSessionId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const handleStartNewGame = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await GameAPI.startNewGame();
      setGameState(response.game_state);
      setStrategyOverlay(response.strategy_overlay || null);
      setAvailableActions(response.available_actions);
      setGameMessage(response.message);
      setSessionId(response.game_state.session_id);
    } catch (error) {
      console.error('Error starting new game:', error);
      setGameMessage('Error starting new game');
    }
    setIsLoading(false);
  }, []);

  const handleMakeAction = useCallback(async (actionType: string, amount?: number) => {
    if (!sessionId) return;
    
    setIsLoading(true);
    try {
      const response = await GameAPI.makeAction(sessionId, actionType, amount || 0);
      setGameState(response.game_state);
      setStrategyOverlay(response.strategy_overlay || null);
      setAvailableActions(response.available_actions);
      setGameMessage(response.message);
    } catch (error) {
      console.error('Error making action:', error);
      setGameMessage('Error making action');
    }
    setIsLoading(false);
  }, [sessionId]);

  const handleNextHand = useCallback(async () => {
    if (!sessionId) return;
    
    setIsLoading(true);
    try {
      const response = await GameAPI.dealNextHand(sessionId);
      setGameState(response.game_state);
      setStrategyOverlay(response.strategy_overlay || null);
      setAvailableActions(response.available_actions);
      setGameMessage(response.message);
    } catch (error) {
      console.error('Error dealing next hand:', error);
      setGameMessage('Error dealing next hand');
    }
    setIsLoading(false);
  }, [sessionId]);

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎯 Quantitative Finance Poker Training</h1>
        <p>Learn quantitative finance concepts through interactive poker gameplay</p>
      </header>

      <main className="app-main">
        {!gameState ? (
          <div className="welcome-screen">
            <div className="welcome-content">
              <h2>Welcome to Quantitative Finance Poker</h2>
              <p>
                This educational poker game teaches quantitative finance concepts through 
                heads-up Texas Hold'em. Each decision point shows you analysis from 6 different 
                quantitative frameworks:
              </p>
              <ul>
                <li><strong>Expected Value (EV)</strong> - Classic profit/loss calculation</li>
                <li><strong>Monte Carlo Simulation</strong> - Statistical outcome modeling</li>
                <li><strong>Bayesian Updating</strong> - Belief revision based on evidence</li>
                <li><strong>Kelly Criterion</strong> - Optimal bet sizing for bankroll growth</li>
                <li><strong>Risk-Adjusted Utility</strong> - Decision making under uncertainty</li>
                <li><strong>Game Theory Optimal (GTO)</strong> - Nash equilibrium strategies</li>
              </ul>
              <button 
                className="start-game-btn"
                onClick={handleStartNewGame}
                disabled={isLoading}
              >
                {isLoading ? 'Starting...' : 'Start New Game'}
              </button>
            </div>
          </div>
        ) : (
          <div className="game-layout">
            <div className="game-area">
              <PokerTable 
                gameState={gameState}
                availableActions={availableActions}
                gameMessage={gameMessage}
                isLoading={isLoading}
                onMakeAction={handleMakeAction}
                onNextHand={handleNextHand}
              />
            </div>
            <div className="strategy-area">
              <StrategyPanel strategyOverlay={strategyOverlay} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App; 