// API service for communicating with the poker backend

import { GameResponse } from '../types/GameTypes';

const API_BASE_URL = 'http://localhost:8000';

export class GameAPI {
  static async startNewGame(): Promise<GameResponse> {
    const response = await fetch(`${API_BASE_URL}/api/game/new`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  static async makeAction(
    sessionId: string, 
    actionType: string, 
    amount: number = 0
  ): Promise<GameResponse> {
    const response = await fetch(`${API_BASE_URL}/api/game/${sessionId}/action`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        action_type: actionType,
        amount: amount || 0,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  static async dealNextHand(sessionId: string): Promise<GameResponse> {
    const response = await fetch(`${API_BASE_URL}/api/game/${sessionId}/next-hand`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  static async getGameStatus(sessionId: string): Promise<GameResponse> {
    const response = await fetch(`${API_BASE_URL}/api/game/${sessionId}/status`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  static async healthCheck(): Promise<{ status: string; message: string }> {
    const response = await fetch(`${API_BASE_URL}/api/health`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
} 