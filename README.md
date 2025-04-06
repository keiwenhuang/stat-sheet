# Basketball Stats Tracking Application

A comprehensive web application for tracking basketball statistics with React frontend, FastAPI backend, and PostgreSQL database.

## Features

- Record detailed player statistics: points, rebounds, assists, steals, blocks, shooting percentages, etc.
- Manage teams, players, games, and seasons
- Calculate standings with advanced tiebreaker system
- View statistical visualizations and dashboards
- Role-based authentication (Admin, League Manager, Stat Keeper)

## Tech Stack

### Backend
- FastAPI (Python 3.13)
- SQLAlchemy ORM
- PostgreSQL
- JWT Authentication

### Frontend
- React 19 with TypeScript
- Material-UI components
- Recharts for data visualization
- React Router for navigation

## Project Structure

```
/stat-sheet/
  /backend/            # FastAPI application
    /app/              # Backend application code
      /api/            # REST API endpoints
      /core/           # Core functionality
      /db/             # Database models and config
      /schemas/        # Pydantic schemas
      /auth/           # Authentication
    main.py            # Main entry point
    requirements.txt   # Python dependencies
  
  /frontend/           # React application
    /src/
      /components/     # React components
      /pages/          # Page components
      /services/       # API integration
      /hooks/          # Custom React hooks
```

## Setup and Installation

### Prerequisites
- Node.js (v18+)
- Python 3.13
- PostgreSQL

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the PostgreSQL database:
   ```bash
   # Create a database named basketball_stats
   ```

4. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at http://localhost:8000, and the API documentation at http://localhost:8000/docs.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The application will be available at http://localhost:5173.

### Using the Start Script

We've included a `start.sh` script to help launch the application:

```bash
# Make the script executable (one-time setup)
chmod +x start.sh

# Run the script
./start.sh
```

This will guide you through starting the backend, frontend, or both servers.

## License

MIT
