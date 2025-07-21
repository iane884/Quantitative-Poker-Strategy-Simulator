#!/bin/bash

echo "🎮 Setting up Quantitative Finance Poker Frontend..."

# Navigate to frontend directory
cd frontend

# Install React dependencies
echo "📦 Installing React dependencies..."
npm install

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "🚀 To start the frontend development server:"
    echo "   cd frontend"
    echo "   npm start"
    echo ""
    echo "🌐 The UI will be available at: http://localhost:3000"
    echo "🔗 Make sure the backend is running at: http://localhost:8000"
    echo ""
    echo "📋 Complete setup instructions:"
    echo "   1. Backend: source venv/bin/activate && python3 run_server.py"
    echo "   2. Frontend: cd frontend && npm start"
    echo "   3. Open: http://localhost:3000"
else
    echo "❌ Failed to install dependencies. Please check the error above."
    exit 1
fi 