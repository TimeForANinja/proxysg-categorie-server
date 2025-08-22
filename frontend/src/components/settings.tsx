import React from 'react';
import {
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Typography,
    Box,
    Button,
    Paper, TableContainer, Table, TableHead, TableRow, TableCell, TableBody
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import BuildCircleIcon from '@mui/icons-material/BuildCircle';
import UploadPage from './upload';
import {getTasks} from "../api/task";
import {ITask} from "../model/types/task"
import {useAuth} from "../model/AuthContext";

interface BuildRowProps {
    task: ITask,
}
/**
 * Renders a table row for a Task entry.
 *
 * Wrapped in React.memo to prevent unnecessary re-renders in the Task table.
 * This works as long as none of the props passed to the Component change
 *
 * The caching also requires us to ensure that all callbacks passed are constants (e.g. wrapped in useCallable)
 */
const BuildRow = React.memo(function BuildRow(props: BuildRowProps) {
    const { task } = props;

    return (
        <TableRow key={task.id}>
            <TableCell>{task.id}</TableCell>
            <TableCell>{task.name}</TableCell>
            <TableCell>{task.status}</TableCell>
        </TableRow>
    );
});

const SettingsPage: React.FC = () => {
    const authMgmt = useAuth();
    const [tasks, setTasks] = React.useState<ITask[]>([]);

    React.useEffect(() => {
        Promise.all([getTasks(authMgmt.token)])
            .then(([taskData]) => {
                // save history to state
                setTasks(taskData);
            })
            .catch((error) => console.error("Error:", error));
    }, [authMgmt]);

    const handleCleanup = () => {
        // Placeholder for future cleanup logic
        // For now, just log to console. This can later call an API.
        // eslint-disable-next-line no-console
        console.log('Cleanup triggered');
    };

    return (
        <Box sx={{ p: 2 }}>
            <Typography variant="h4" gutterBottom>
                Settings
            </Typography>

            <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <BuildCircleIcon fontSize="small" /> Task History
                    </Typography>
                </AccordionSummary>
                <AccordionDetails>
                    <Paper elevation={0} sx={{ p: 0 }}>
                        <TableContainer component={Paper} style={{maxHeight: 'calc(100vh - 190px)', overflow: 'auto'}}>
                            <Table sx={{minWidth: 650}} size="small" stickyHeader>
                                <TableHead>
                                    <TableRow>
                                        <TableCell component="th" scope="row">ID</TableCell>
                                        <TableCell>Name</TableCell>
                                        <TableCell>State</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {tasks.map(task =>
                                        <BuildRow task={task} />
                                    )}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>
                </AccordionDetails>
            </Accordion>

            <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <BuildCircleIcon fontSize="small" /> Upload Task
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
                        Perform maintenance tasks to clean up old data or temporary resources. (Placeholder)
                    </Typography>
                    <Button variant="contained" color="warning" onClick={handleCleanup}>
                        Run Cleanup
                    </Button>
                </AccordionDetails>
            </Accordion>
        </Box>
    );
};

export default SettingsPage;
