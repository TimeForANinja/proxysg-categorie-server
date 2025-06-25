import React from 'react';
import Grid from "@mui/material/Grid2";

import {getHistory, ICommits} from "../api/history";
import {useAuth} from "../model/AuthContext";
import HistoryTable from "./shared/HistoryTable";
import {Box, Button} from "@mui/material";
import {startCommit} from "../api/task";
import TaskStatus from "./shared/TaskStatus";


function HistoryPage() {
    const { token } = useAuth();
    const [commits, setCommits] = React.useState<ICommits[]>([]);

    // ID (or empty) of ongoing commit task
    const [taskId, setTaskId] = React.useState<string>("");

    React.useEffect(() => {
        Promise.all([getHistory(token)])
            .then(([commitData]) => {
                // save history to state
                setCommits(commitData);
            })
            .catch((error) => console.error("Error:", error));
    }, [token]);


    const onCommit = async () => {
        const newTaskId = await startCommit(token);
        setTaskId(newTaskId);
    }

    return (
        <>

            <Grid
                container
                spacing={1}
                justifyContent="center"
                alignItems="center"
            >
                { /* Add-Button */ }
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
                        onTaskComplete={() => setTaskId("")}
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
