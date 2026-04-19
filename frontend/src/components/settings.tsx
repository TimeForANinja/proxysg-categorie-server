import React, {useEffect, useState} from 'react';
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Box,
    Button,
    Container,
    Grid,
    Paper, Stack,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import BuildCircleIcon from '@mui/icons-material/BuildCircle';
import BarChartIcon from '@mui/icons-material/BarChart';
import {resetBranches} from "../api/branch";
import {useAuth} from "../hooks/useLogin";
import {useBranch} from "../hooks/useBranch";
import UploadPage from "./shared/upload";
import {getMetrics, IMetricsData} from "../api/metrics";


const SettingsPage: React.FC = () => {
    const authMgmt = useAuth();
    const { isLocked } = useBranch();
    const [metrics, setMetrics] = useState<IMetricsData>({});

    const refreshMetrics = async () => {
        try {
            const data = await getMetrics(authMgmt.token);
            setMetrics(data);
        } catch (e) {
            console.error("Failed to fetch metrics", e);
        }
    };

    useEffect(() => {
        refreshMetrics();
    }, []);

    const onResetBranchPressed = () => {
        resetBranches(authMgmt.token);
    };

    return (
        <Container maxWidth="md" sx={{ mt: 4 }}>
            <Paper elevation={3} sx={{ p: 4 }}>
                <Typography variant="h4" gutterBottom>
                    Settings
                </Typography>

                <Box sx={{ mt: 1 }}>
                    <Grid container spacing={3}>
                        <Grid size={12}>
                            <Accordion>
                                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                    <Typography sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        <BarChartIcon fontSize="small" /> Metrics
                                    </Typography>
                                </AccordionSummary>
                                <AccordionDetails>
                                    <TableContainer component={Paper} variant="outlined">
                                        <Table size="small">
                                            <TableHead>
                                                <TableRow>
                                                    <TableCell sx={{ fontWeight: 'bold' }}>Metric</TableCell>
                                                    <TableCell sx={{ fontWeight: 'bold' }}>Value</TableCell>
                                                </TableRow>
                                            </TableHead>
                                            <TableBody>
                                                {Object.entries(metrics).map(([key, value]) => (
                                                    <TableRow key={key}>
                                                        <TableCell>{key}</TableCell>
                                                        <TableCell>{String(value)}</TableCell>
                                                    </TableRow>
                                                ))}
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                    <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                                        <Button variant="outlined" size="small" onClick={refreshMetrics}>
                                            Refresh
                                        </Button>
                                    </Box>
                                </AccordionDetails>
                            </Accordion>

                            <Accordion>
                                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                    <Typography sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        <BuildCircleIcon fontSize="small" /> Upload LocalDB
                                    </Typography>
                                </AccordionSummary>
                                <AccordionDetails>
                                    {/* Reuse the existing UploadPage UI inside the settings */}
                                    {/* Wrapped in a Paper-less Box to better fit within the accordion */}
                                    <Paper elevation={0} sx={{ p: 0 }}>
                                        <UploadPage />
                                    </Paper>
                                </AccordionDetails>
                            </Accordion>

                            <Accordion>
                                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                    <Typography sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        <BuildCircleIcon fontSize="small" /> Cleanup
                                    </Typography>
                                </AccordionSummary>
                                <AccordionDetails>
                                    <Typography variant="body1" sx={{ mb: 2 }}>
                                        Perform various maintenance tasks.
                                    </Typography>
                                    <Stack spacing={2} sx={{ mb: 2 }}>
                                        <Button variant="contained" color="warning" onClick={onResetBranchPressed} disabled={isLocked}>
                                            Reset User-Branch
                                        </Button>
                                    </Stack>
                                </AccordionDetails>
                            </Accordion>
                        </Grid>
                    </Grid>
                </Box>
            </Paper>
        </Container>
    );
};

export default SettingsPage;
