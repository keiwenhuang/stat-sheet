import { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import CircularProgress from '@mui/material/CircularProgress';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import {
    PeopleAlt,
    SportsBasketball,
    EmojiEvents,
    ShowChart
} from '@mui/icons-material';
import StatCard from './StatCard';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Mock data - will be replaced with API calls
const mockStats = {
    totalTeams: 8,
    totalPlayers: 96,
    totalGames: 24,
    completedGames: 18,
    upcomingGames: 6,
};

const mockTopScorers = [
    { id: 1, name: 'James Johnson', team: 'Lakers', points: 28.5 },
    { id: 2, name: 'Michael Smith', team: 'Warriors', points: 26.3 },
    { id: 3, name: 'David Williams', team: 'Celtics', points: 25.7 },
    { id: 4, name: 'Robert Brown', team: 'Heat', points: 24.1 },
    { id: 5, name: 'William Davis', team: 'Bulls', points: 23.8 },
];

const mockTeamStats = [
    { name: 'Lakers', wins: 7, losses: 2 },
    { name: 'Warriors', wins: 6, losses: 3 },
    { name: 'Celtics', wins: 6, losses: 3 },
    { name: 'Heat', wins: 5, losses: 4 },
    { name: 'Bulls', wins: 5, losses: 4 },
    { name: 'Raptors', wins: 4, losses: 5 },
    { name: 'Nets', wins: 3, losses: 6 },
    { name: 'Spurs', wins: 2, losses: 7 },
];

const Dashboard = () => {
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState(mockStats);
    const [topScorers, setTopScorers] = useState(mockTopScorers);
    const [teamStats, setTeamStats] = useState(mockTeamStats);

    useEffect(() => {
        // Simulate API call
        const timer = setTimeout(() => {
            setLoading(false);
        }, 1000);

        return () => clearTimeout(timer);
    }, []);

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box>
            <Typography variant="h4" gutterBottom>
                Dashboard
            </Typography>

            {/* Key Statistics */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Teams"
                        value={stats.totalTeams}
                        icon={<PeopleAlt />}
                        color="#1976d2"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Players"
                        value={stats.totalPlayers}
                        icon={<PeopleAlt />}
                        color="#2e7d32"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Games Played"
                        value={stats.completedGames}
                        icon={<SportsBasketball />}
                        color="#ed6c02"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Upcoming Games"
                        value={stats.upcomingGames}
                        icon={<EmojiEvents />}
                        color="#9c27b0"
                    />
                </Grid>
            </Grid>

            {/* Charts and Tables */}
            <Grid container spacing={3}>
                {/* Team Standings Bar Chart */}
                <Grid item xs={12} md={8}>
                    <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
                        <Typography variant="h6" gutterBottom>
                            Team Standings
                        </Typography>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart
                                data={teamStats}
                                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="wins" fill="#4caf50" name="Wins" />
                                <Bar dataKey="losses" fill="#f44336" name="Losses" />
                            </BarChart>
                        </ResponsiveContainer>
                    </Paper>
                </Grid>

                {/* Top Scorers Table */}
                <Grid item xs={12} md={4}>
                    <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
                        <Typography variant="h6" gutterBottom>
                            Top Scorers
                        </Typography>
                        <TableContainer>
                            <Table size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Player</TableCell>
                                        <TableCell>Team</TableCell>
                                        <TableCell align="right">PPG</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {topScorers.map((player) => (
                                        <TableRow key={player.id}>
                                            <TableCell>{player.name}</TableCell>
                                            <TableCell>{player.team}</TableCell>
                                            <TableCell align="right">{player.points}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default Dashboard;
