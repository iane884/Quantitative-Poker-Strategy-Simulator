# 🎯 Quantitative Finance Poker Training App - Complete Setup

A full-stack educational poker application that teaches quantitative finance concepts through interactive gameplay.

## 🎮 **What You Get**

### **🎨 Beautiful Web UI**
- 🃏 Visual poker table with cards and actions
- 📊 Real-time strategy analysis panel
- 🎯 Interactive buttons for making poker decisions
- 📱 Responsive design that works on desktop and mobile

### **🧠 6 Quantitative Strategies**
Each decision shows analysis from:
- 💰 **Expected Value (EV)** - Classic profit/loss calculations
- 🎲 **Monte Carlo Simulation** - 1000+ random scenario simulations  
- 🧠 **Bayesian Updating** - Belief revision based on opponent actions
- 📈 **Kelly Criterion** - Optimal bet sizing for bankroll growth
- ⚖️ **Risk-Adjusted Utility** - Mean-variance optimization
- 🎯 **Game Theory Optimal (GTO)** - Nash equilibrium strategies

## 🚀 **Quick Start (2 Steps)**

### **Step 1: Start the Backend**
```bash
# In terminal 1 - Backend API
source venv/bin/activate
python3 run_server.py
```
**Backend will run at:** http://localhost:8000

### **Step 2: Start the Frontend** 
```bash
# In terminal 2 - Frontend UI
chmod +x setup_frontend.sh
./setup_frontend.sh
cd frontend
npm start
```
**Frontend will run at:** http://localhost:3000

## 🎮 **How to Play**

1. **Open your browser** to http://localhost:3000
2. **Click "Start New Game"** 
3. **See your cards** and the strategy recommendations
4. **Click any action button** (Fold, Call, Raise, etc.)
5. **Watch the bot respond** with EV-based logic
6. **Learn from the detailed analysis** shown for each decision

## 📊 **Strategy Analysis Example**

When it's your turn, you'll see something like:

### 💰 **Expected Value Strategy**
- **Recommendation:** CALL (+$23.50 EV)
- **Calculation:** 0.65 × $125 - 0.35 × $25 = +$23.50
- **Explanation:** Positive expected value makes this profitable long-term

### 🎲 **Monte Carlo Strategy** 
- **Recommendation:** CALL (Win 65% of 1000 simulations)
- **Results:** 650 wins, 18 ties, 332 losses
- **Explanation:** Strong win rate supports calling

### 🧠 **Bayesian Strategy**
- **Recommendation:** FOLD (Opponent 73% likely strong)
- **Prior:** 25% strong hand → **Updated:** 73% after their raise
- **Explanation:** Opponent's aggressive action suggests strength

*...and 3 more strategies with detailed analysis!*

## 🔧 **Detailed Setup Instructions**

### **Prerequisites**
- Python 3.8+ 
- Node.js 14+ and npm
- Terminal/Command Line

### **Backend Setup**
```bash
# 1. Navigate to project
cd "/Users/ian.evensen/Documents/PPs/poker app"

# 2. Activate virtual environment (if not already active)
source venv/bin/activate

# 3. Install Python dependencies (if not done)
pip install fastapi uvicorn pydantic deuces

# 4. Start backend server
python3 run_server.py
```

### **Frontend Setup**
```bash
# 1. Install React dependencies
cd frontend
npm install

# 2. Start development server
npm start
```

### **Verification**
- **Backend Health:** http://localhost:8000/api/health
- **API Docs:** http://localhost:8000/docs
- **Frontend UI:** http://localhost:3000

## 🎯 **Features**

### **🎮 Game Features**
- ✅ Heads-up Texas Hold'em
- ✅ Visual card display with suits (♠♥♦♣)
- ✅ Real-time pot and stack tracking
- ✅ Multiple betting options per decision
- ✅ Hand-by-hand progression
- ✅ Win/loss tracking

### **📊 Educational Features**
- ✅ 6 different quantitative frameworks
- ✅ Step-by-step mathematical calculations
- ✅ Real-time strategy comparisons
- ✅ Expandable detailed analysis
- ✅ Confidence levels for each recommendation
- ✅ Educational tooltips and explanations

### **🤖 Bot Features**
- ✅ EV-based decision making
- ✅ Transparent reasoning shown to user
- ✅ Consistent mathematical approach
- ✅ Educational explanations for bot actions

## 🔍 **Troubleshooting**

### **Backend Issues**
```bash
# If imports fail:
source venv/bin/activate
pip install fastapi uvicorn pydantic deuces

# If server won't start:
python3 -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

### **Frontend Issues**
```bash
# If npm install fails:
cd frontend
rm -rf node_modules package-lock.json
npm install

# If React won't start:
npm start
```

### **Connection Issues**
- Backend must run on port 8000
- Frontend must run on port 3000  
- Check firewall settings if needed

## 🎯 **What Makes This Special**

This isn't just a poker game - it's a **quantitative finance education platform**:

- **📚 Learn by Doing:** See Kelly Criterion, Bayesian inference, and utility theory in action
- **🔍 Compare Approaches:** Watch how different frameworks reach different conclusions
- **📊 See the Math:** Every recommendation shows detailed calculations
- **🎮 Stay Engaged:** Learn through interactive gameplay, not textbooks
- **🧠 Build Intuition:** Develop quantitative thinking through repeated decisions

## 🚀 **Ready to Learn!**

Your complete quantitative finance poker trainer is ready! The combination of visual gameplay and mathematical analysis provides an engaging way to learn advanced finance concepts through practical decision-making.

**Start both servers and visit http://localhost:3000 to begin!** 🎉 