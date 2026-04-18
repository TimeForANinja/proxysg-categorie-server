import React from 'react';
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Box,
    Button,
    Container,
    Grid,
    Paper, Stack,
    Typography
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import BuildCircleIcon from '@mui/icons-material/BuildCircle';
import {resetBranches} from "../api/branch";
import {useAuth} from "../hooks/useLogin";
import UploadPage from "./shared/upload";


const SettingsPage: React.FC = () => {
    const authMgmt = useAuth();

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
                                        <Button variant="contained" color="warning" onClick={onResetBranchPressed}>
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
