# Quantitative Finance Poker Training App

An educational poker game that teaches quantitative finance concepts through interactive heads-up Texas Hold'em play.

## Features

- Heads-up No-Limit Texas Hold'em against an EV-based bot
- Real-time strategy overlays showing 6 quantitative frameworks:
  - Expected Value (EV)
  - Monte Carlo Simulation
  - Bayesian Updating
  - Kelly Criterion
  - Risk-Adjusted Utility
  - Game Theory Optimal (GTO)

## Setup

### Backend
```bash
pip install -r requirements.txt
python run_server.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Architecture

- **Backend**: FastAPI with poker game logic and strategy calculations
- **Frontend**: React with TypeScript for the user interface
- **Poker Engine**: Uses deuces library for hand evaluation and Monte Carlo simulations
- **Strategy Engine**: Implements all 6 quantitative frameworks with real-time calculations

## Game Flow

1. Each hand starts with fixed stacks (100 units)
2. User plays heads-up against EV-based bot
3. Strategy sidebar updates on each user decision point
4. Each strategy provides recommendations with detailed calculations
5. Session-based play (no accounts needed) 