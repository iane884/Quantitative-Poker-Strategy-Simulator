// Type definitions for the Poker Training App

export interface Card {
  rank: string; // '2'-'9', 'T', 'J', 'Q', 'K', 'A'
  suit: string; // 'h', 'd', 'c', 's'
}

export interface PlayerAction {
  action_type: string;
  amount: number;
  player: string;
}

export interface GameState {
  session_id: string;
  street: string; // 'preflop', 'flop', 'turn', 'river'
  pot_size: number;
  user_stack: number;
  bot_stack: number;
  user_cards: Card[];
  bot_cards?: Card[];  // Only present when hand is over
  community_cards: Card[];
  current_bet: number;
  to_call: number;
  active_player: string;
  action_history: PlayerAction[];
  hand_number: number;
  is_hand_over: boolean;
  winner?: string;
}

export interface AvailableAction {
  action_type: string;
  amount?: number;
  description: string;
}

export interface StrategyRecommendation {
  strategy_name: string;
  recommended_action: string;
  recommended_amount?: number;
  explanation: string;
  formula: string;
  variables: Record<string, any>;
  calculation_steps: string[];
  confidence: number;
}

export interface StrategyOverlay {
  ev_strategy: StrategyRecommendation;
  monte_carlo_strategy: StrategyRecommendation;
  bayesian_strategy: StrategyRecommendation;
  kelly_strategy: StrategyRecommendation;
  risk_utility_strategy: StrategyRecommendation;
  gto_strategy: StrategyRecommendation;
}

export interface GameResponse {
  game_state: GameState;
  available_actions: AvailableAction[];
  strategy_overlay?: StrategyOverlay;
  message: string;
} 