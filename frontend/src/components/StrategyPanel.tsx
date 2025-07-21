import React, { useState } from 'react';
import { StrategyOverlay } from '../types/GameTypes';

interface StrategyPanelProps {
  strategyOverlay: StrategyOverlay | null;
}

const StrategyPanel: React.FC<StrategyPanelProps> = ({ strategyOverlay }) => {
  const [expandedStrategy, setExpandedStrategy] = useState<string | null>(null);

  if (!strategyOverlay) {
    return (
      <div className="strategy-panel">
        <div className="strategy-header">
          <h2>📊 Strategy Analysis</h2>
        </div>
        <div style={{ padding: '2rem', textAlign: 'center', color: '#9ca3af' }}>
          <p>Strategy recommendations will appear here when it's your turn to act.</p>
        </div>
      </div>
    );
  }

  const strategies = [
    { key: 'ev_strategy', data: strategyOverlay.ev_strategy, icon: '💰', color: '#60a5fa' },
    { key: 'monte_carlo_strategy', data: strategyOverlay.monte_carlo_strategy, icon: '🎲', color: '#34d399' },
    { key: 'bayesian_strategy', data: strategyOverlay.bayesian_strategy, icon: '🧠', color: '#f59e0b' },
    { key: 'kelly_strategy', data: strategyOverlay.kelly_strategy, icon: '📈', color: '#8b5cf6' },
    { key: 'risk_utility_strategy', data: strategyOverlay.risk_utility_strategy, icon: '⚖️', color: '#ef4444' },
    { key: 'gto_strategy', data: strategyOverlay.gto_strategy, icon: '🎯', color: '#06b6d4' },
  ];

  const toggleStrategy = (strategyKey: string) => {
    setExpandedStrategy(expandedStrategy === strategyKey ? null : strategyKey);
  };

  const getActionColor = (action: string) => {
    const colors: Record<string, string> = {
      'fold': '#ef4444',
      'call': '#10b981',
      'check': '#6366f1',
      'bet': '#8b5cf6',
      'raise': '#f59e0b',
      'all_in': '#dc2626'
    };
    return colors[action.toLowerCase()] || '#6b7280';
  };

  return (
    <div className="strategy-panel">
      <div className="strategy-header">
        <h2>📊 Strategy Analysis</h2>
        <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem', color: '#94a3b8' }}>
          Quantitative recommendations for your decision
        </p>
      </div>

      <div className="strategy-list">
        {strategies.map(({ key, data, icon, color }) => (
          <div key={key} className="strategy-card">
            <div 
              className="strategy-card-header"
              onClick={() => toggleStrategy(key)}
              style={{ borderLeft: `4px solid ${color}` }}
            >
              <div>
                <div className="strategy-name">
                  {icon} {data.strategy_name}
                </div>
                <div 
                  className="strategy-recommendation"
                  style={{ color: getActionColor(data.recommended_action) }}
                >
                  <strong>{data.recommended_action.toUpperCase()}</strong>
                  {data.recommended_amount && ` $${data.recommended_amount}`}
                  <span style={{ color: '#9ca3af', marginLeft: '0.5rem' }}>
                    (Confidence: {(data.confidence * 100).toFixed(0)}%)
                  </span>
                </div>
              </div>
              <div style={{ color: '#9ca3af', fontSize: '1.2rem' }}>
                {expandedStrategy === key ? '▼' : '▶'}
              </div>
            </div>

            {expandedStrategy === key && (
              <div className="strategy-details">
                <div className="strategy-explanation">
                  {data.explanation}
                </div>

                <div className="strategy-formula">
                  <strong>Formula:</strong> {data.formula}
                </div>

                <div className="calculation-steps">
                  <h4>Calculation Steps:</h4>
                  <ol>
                    {data.calculation_steps.map((step, index) => (
                      <li key={index}>{step}</li>
                    ))}
                  </ol>
                </div>

                <div className="strategy-variables">
                  <h4 style={{ marginBottom: '0.5rem', color: '#9ca3af', fontSize: '0.9rem' }}>
                    Key Variables:
                  </h4>
                  {Object.entries(data.variables).map(([key, value]) => (
                    <div key={key} className="variable-item">
                      <span className="variable-name">{key.replace(/_/g, ' ')}:</span>
                      <span className="variable-value">{String(value)}</span>
                    </div>
                  ))}
                </div>

                <div className="confidence-bar">
                  <div className="confidence-label">
                    Confidence Level: {(data.confidence * 100).toFixed(1)}%
                  </div>
                  <div className="confidence-progress">
                    <div 
                      className="confidence-fill"
                      style={{ width: `${data.confidence * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div style={{ 
        padding: '1rem', 
        fontSize: '0.8rem', 
        color: '#6b7280', 
        borderTop: '1px solid #374151',
        marginTop: '1rem'
      }}>
        <p style={{ margin: 0 }}>
          💡 <strong>Tip:</strong> Each strategy offers a different perspective on the same decision. 
          Compare their reasoning to develop a deeper understanding of quantitative decision-making.
        </p>
      </div>
    </div>
  );
};

export default StrategyPanel; 