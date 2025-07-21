import React from 'react';
import { GameState, AvailableAction, Card } from '../types/GameTypes';

interface PokerTableProps {
  gameState: GameState;
  availableActions: AvailableAction[];
  gameMessage: string;
  isLoading: boolean;
  onMakeAction: (actionType: string, amount?: number) => void;
  onNextHand: () => void;
}

const PokerTable: React.FC<PokerTableProps> = ({
  gameState,
  availableActions,
  gameMessage,
  isLoading,
  onMakeAction,
  onNextHand,
}) => {
  const renderCard = (card: Card | null, index: number) => {
    if (!card) {
      return (
        <div key={index} className="card card-back">
          <div className="card-content">?</div>
        </div>
      );
    }

    const suitSymbol: { [key: string]: string } = {
      'h': '♥',
      'd': '♦',
      'c': '♣',
      's': '♠'
    };

    const symbol = suitSymbol[card.suit] || card.suit;
    const suitClass = ['h', 'd'].includes(card.suit) ? 'suit-hearts' : 'suit-clubs';

    return (
      <div key={index} className={`card ${suitClass}`}>
        <div className="card-content">
          <div className="card-rank">{card.rank}</div>
          <div className="card-suit">{symbol}</div>
        </div>
      </div>
    );
  };

  const renderCommunityCards = () => {
    const cards: (Card | null)[] = [...gameState.community_cards];
    while (cards.length < 5) {
      cards.push(null); // Add empty slots
    }
    return cards.map((card, index) => renderCard(card, index));
  };

  const handleActionClick = (action: AvailableAction) => {
    onMakeAction(action.action_type, action.amount || 0);
  };

  const getActionButtonClass = (actionType: string) => {
    return `action-btn ${actionType.toLowerCase()}`;
  };

  return (
    <div className="poker-table">
      {/* Pot Display */}
      <div className="pot-display">
        💰 Pot: ${gameState.pot_size}
        <div style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
          Street: {gameState.street.toUpperCase()}
          {gameState.to_call > 0 && ` | To call: $${gameState.to_call}`}
        </div>
      </div>

      {/* Community Cards */}
      <div className="board">
        <h3>Community Cards</h3>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          {renderCommunityCards()}
        </div>
      </div>

      {/* Bot Section */}
      <div className="player-section">
        <h3>🤖 Bot (Stack: ${gameState.bot_stack})</h3>
        <div className="player-cards">
          {gameState.bot_cards ? (
            // Show real cards when hand is over
            gameState.bot_cards.map((card, index) => renderCard(card, index))
          ) : (
            // Show hidden cards during play
            <>
              <div className="card" style={{ backgroundColor: '#374151' }}>
                <div className="card-content">
                  <div className="card-rank">?</div>
                  <div className="card-suit">?</div>
                </div>
              </div>
              <div className="card" style={{ backgroundColor: '#374151' }}>
                <div className="card-content">
                  <div className="card-rank">?</div>
                  <div className="card-suit">?</div>
                </div>
              </div>
            </>
          )}
        </div>
        <div style={{ color: gameState.active_player === 'bot' ? '#60a5fa' : '#9ca3af' }}>
          {gameState.active_player === 'bot' ? '← Bot\'s turn' : 'Waiting...'}
          {gameState.is_hand_over && gameState.bot_cards && (
            <div style={{ fontSize: '0.9rem', marginTop: '0.5rem', color: '#fbbf24' }}>
              🔍 Bot's cards revealed!
            </div>
          )}
        </div>
      </div>

      {/* User Section */}
      <div className="player-section">
        <h3>👤 You (Stack: ${gameState.user_stack})</h3>
        <div className="player-cards">
          {gameState.user_cards.map((card, index) => renderCard(card, index))}
        </div>
        <div style={{ color: gameState.active_player === 'user' ? '#60a5fa' : '#9ca3af' }}>
          {gameState.active_player === 'user' ? '← Your turn' : 'Waiting...'}
        </div>
      </div>

      {/* Game Actions */}
      {!gameState.is_hand_over && gameState.active_player === 'user' && (
        <div className="game-actions">
          <h4>Choose Your Action:</h4>
          <div className="action-buttons">
            {availableActions.map((action, index) => (
              <button
                key={index}
                className={getActionButtonClass(action.action_type)}
                onClick={() => handleActionClick(action)}
                disabled={isLoading}
              >
                {action.description}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Next Hand Button */}
      {gameState.is_hand_over && (
        <div className="game-actions">
          <h4>
            {gameState.winner === 'user' ? '🎉 You won!' : 
             gameState.winner === 'bot' ? '🤖 Bot won!' : '🤝 Split pot!'}
          </h4>
          <button
            className="next-hand-btn"
            onClick={onNextHand}
            disabled={isLoading}
          >
            {isLoading ? 'Dealing...' : 'Deal Next Hand'}
          </button>
        </div>
      )}

      {/* Game Message */}
      {gameMessage && (
        <div className="game-message">
          {gameMessage}
        </div>
      )}

      {/* Game Info */}
      <div style={{ 
        marginTop: '2rem', 
        padding: '1rem', 
        background: '#374151', 
        borderRadius: '8px',
        fontSize: '0.9rem',
        color: '#d1d5db'
      }}>
        <div><strong>Hand #:</strong> {gameState.hand_number}</div>
        <div><strong>Session:</strong> {gameState.session_id.slice(0, 8)}...</div>
        <div><strong>Actions this hand:</strong> {gameState.action_history.length}</div>
      </div>
    </div>
  );
};

export default PokerTable; 