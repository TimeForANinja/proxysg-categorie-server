import React from 'react';
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Box,
    Button,
    Container,
    Paper, Stack,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography
} from '@mui/material';
import Grid from "@mui/material/Grid2";
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import BuildCircleIcon from '@mui/icons-material/BuildCircle';
import UploadPage from './shared/upload';
import {getTasks} from "../api/task";
import {ITask} from "../model/types/task"
import {useAuth} from "../model/AuthContext";
import {CleanupFlags, cleanupUnused} from "../api/task_new";
import {TaskStatusTracker} from "./shared/TaskStatusTracker";

interface BuildRowProps {
    task: ITask,
}
/**
 * Renders a table row for a Task entry.
 *
 * Wrapped in React.memo to prevent unnecessary re-renders in the Task table.
 * This works as long as none of the props passed to the Component change
 *
 * The caching also requires us to ensure that all callbacks passed are constants (e.g., wrapped in useCallable)
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
    const [taskId, setTaskId] = React.useState<string>("");

    React.useEffect(() => {
        Promise.all([getTasks(authMgmt.token)])
            .then(([taskData]) => {
                // save history to state
                setTasks(taskData.sort((a, b) => b.created_at - a.created_at));
            })
            .catch((error) => console.error("Error:", error));
    }, [authMgmt]);

    const onCleanupURLsPressed = () => {
        cleanupUnused(authMgmt.token, CleanupFlags.URLs).then(tid => {
            setTaskId(tid);
        })
    };

    const onCleanupCATsPressed = () => {
        cleanupUnused(authMgmt.token, CleanupFlags.Categories).then(tid => {
            setTaskId(tid);
        })
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
                                                        <BuildRow key={task.id} task={task} />
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
                                        Perform various maintenance tasks, like cleaning up unused DB data.
                                    </Typography>
                                    <Stack spacing={2} sx={{ mb: 2 }}>
                                        <Button variant="contained" color="warning" onClick={onCleanupURLsPressed}>
                                            Schedule Cleanup of Unused URLs
                                        </Button>
                                        <Button variant="contained" color="warning" onClick={onCleanupCATsPressed}>
                                            Schedule Cleanup of Unused Categories
                                        </Button>
                                    </Stack>
                                </AccordionDetails>
                            </Accordion>
                        </Grid>

                        <Grid size={12}>
                            {/* Generic task status tracker to handle banner messages based on task status */}
                            <TaskStatusTracker
                                title="URL Cleanup"
                                taskId={taskId}
                                onComplete={() => {
                                    // clear the taskID once the task completes
                                    setTaskId("");
                                }}
                            />
                        </Grid>
                    </Grid>
                </Box>
            </Paper>
        </Container>
    );
};

export default SettingsPage;
