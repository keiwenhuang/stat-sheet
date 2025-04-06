import { Paper, Typography, Box } from '@mui/material';

interface StatCardProps {
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color?: string;
}

const StatCard = ({ title, value, icon, color = '#1976d2' }: StatCardProps) => {
    return (
        <Paper
            elevation={2}
            sx={{
                p: 2,
                display: 'flex',
                alignItems: 'center',
                height: '100%',
                borderLeft: `4px solid ${color}`,
            }}
        >
            <Box
                sx={{
                    backgroundColor: `${color}15`, // using transparency
                    borderRadius: '50%',
                    p: 1.5,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: color,
                    mr: 2,
                }}
            >
                {icon}
            </Box>
            <Box>
                <Typography variant="body2" color="text.secondary">
                    {title}
                </Typography>
                <Typography variant="h5" component="div" fontWeight="bold">
                    {value}
                </Typography>
            </Box>
        </Paper>
    );
};

export default StatCard;
