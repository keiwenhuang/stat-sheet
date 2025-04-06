#!/bin/bash
# Start script for Basketball Stats Tracking Application

echo "Basketball Stats Tracking App Launcher"
echo "====================================="
echo ""

# Check if PostgreSQL is running
echo "Checking PostgreSQL status..."
pg_running=$(pg_isready 2>/dev/null && echo "yes" || echo "no")

if [ "$pg_running" == "no" ]; then
  echo "⚠️  PostgreSQL does not appear to be running."
  echo "Please start PostgreSQL before continuing."
  echo ""
fi

# Function to start backend
start_backend() {
  echo "Starting FastAPI backend server..."
  cd backend
  uvicorn main:app --reload
}

# Function to start frontend
start_frontend() {
  echo "Starting React frontend dev server..."
  cd frontend
  npm run dev
}

# Prompt user for what to start
echo "What would you like to start?"
echo "1) Backend server only"
echo "2) Frontend server only"
echo "3) Both (in separate terminals)"
echo "4) Exit"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
  1)
    start_backend
    ;;
  2)
    start_frontend
    ;;
  3)
    echo "Starting both servers in separate terminals..."
    osascript -e 'tell application "Terminal" to do script "cd '$PWD' && cd backend && uvicorn main:app --reload"' 
    osascript -e 'tell application "Terminal" to do script "cd '$PWD' && cd frontend && npm run dev"'
    echo "Servers started in separate terminal windows."
    ;;
  4)
    echo "Exiting..."
    exit 0
    ;;
  *)
    echo "Invalid choice. Exiting."
    exit 1
    ;;
esac
