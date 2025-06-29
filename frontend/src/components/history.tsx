import React from 'react';
import Grid from "@mui/material/Grid2";

import {getHistory, ICommits} from "../api/history";
import {useAuth} from "../model/AuthContext";
import HistoryTable from "./shared/HistoryTable";
import {Box, Button, TextField} from "@mui/material";
import {startCommit} from "../api/task";
import TaskStatus from "./shared/TaskStatus";


function HistoryPage() {
    const { token } = useAuth();
    const [commits, setCommits] = React.useState<ICommits[]>([]);

    // ID (or empty) of ongoing commit task
    const [taskId, setTaskId] = React.useState<string>("");

    // State for commit message
    const [commitMessage, setCommitMessage] = React.useState<string>("");

    React.useEffect(() => {
        Promise.all([getHistory(token)])
            .then(([commitData]) => {
                // save history to state
                setCommits(commitData);
            })
            .catch((error) => console.error("Error:", error));
    }, [token]);


    const onCommit = async () => {
        if (!commitMessage.trim()) {
            alert("Please enter a commit message");
            return;
        }
        const newTaskId = await startCommit(token, commitMessage);
        setTaskId(newTaskId);
        setCommitMessage(""); // Clear the commit message after submission
    }

    const onTaskDone = (success: boolean) => {
        setTaskId("");
        // Reload the history data
        if (success) {
            getHistory(token)
                .then((commitData) => {
                    setCommits(commitData);
                })
                .catch((error) => console.error("Error:", error));
        }

    }

    return (
        <>

            <Grid
                container
                spacing={1}
                justifyContent="center"
                alignItems="center"
            >
                { /* Commit Message Input */ }
                <Grid size={8}>
                    <Box style={{padding: 2}} display="flex" flexDirection="column" gap={2}>
                        <TextField
                            margin="dense"
                            label="Commit Message"
                            size="small"
                            variant="filled"
                            value={commitMessage}
                            onChange={(e) => setCommitMessage(e.target.value)}
                        />
                    </Box>
                </Grid>

                { /* Commit Button */ }
                <Grid size={3}>
                    <Box style={{padding: 2}} display="flex" flexDirection="column" gap={2}>
                        <Button
                            variant="outlined"
                            onClick={() => onCommit()}
                        >Commit</Button>
                    </Box>
                </Grid>

                <Grid size={12}>
                    <TaskStatus 
                        taskId={taskId} 
                        successMessage="Commit completed successfully!" 
                        failureMessage="Commit failed. Please try again."
                        onTaskComplete={onTaskDone}
                    />
                </Grid>

                <Grid size={12}>
                    <HistoryTable
                        commits={commits}
                    />
                </Grid>
            </Grid>
        </>
    );
}

export default HistoryPage;
