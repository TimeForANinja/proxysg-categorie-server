import React from 'react';
import Grid from "@mui/material/Grid";

import {getHistory} from "../api/history";
import HistoryTable from "./shared/HistoryTable";
import {useBranch} from "../hooks/useBranch";
import {IRestCommit} from "../types/history";
import {useAuth} from "../hooks/useLogin";
import {Box, Button, TextField} from "@mui/material";
import {doCommit} from "../api/branch";
import {useNotification} from "../hooks/useNotification";

function HistoryPage() {
    const authMgmt = useAuth();
    const { currentBranch, isLocked } = useBranch();
    const { showError } = useNotification();

    const [commits, setCommits] = React.useState<IRestCommit[]>([]);

    // State for the commit message
    const [commitMessage, setCommitMessage] = React.useState<string>("");

    const fetchData = React.useCallback(() => {
        getHistory(authMgmt.token, currentBranch)
            .then((commitData) => {
                // save history to state
                setCommits(commitData);
            })
            .catch((error) => console.error("Error:", error));
    }, [currentBranch]);

    React.useEffect(() => {
        fetchData();
    }, [fetchData]);

    const onCommit = async () => {
        if (!commitMessage.trim()) {
            showError("Please enter a commit message");
            return;
        }
        await doCommit(authMgmt.token, commitMessage);
        setCommitMessage(""); // Clear the commit message after submission
        fetchData();
    };

    return (
        <>
            <Grid
                container
                spacing={1}
                sx={{ justifyContent: "center", alignItems: "center" }}
            >
                { /* Commit Message Input and Button - only show if branch is not locked */ }
                {!isLocked && (
                    <>
                        <Grid size={8}>
                            <Box sx={{ p: 2, display: "flex", flexDirection: "column", gap: 2 }}>
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

                        <Grid size={3}>
                            <Box sx={{ p: 2, display: "flex", flexDirection: "column", gap: 2 }}>
                                <Button
                                    variant="outlined"
                                    onClick={() => onCommit()}
                                >Commit</Button>
                            </Box>
                        </Grid>
                    </>
                )}

                { /* Table of recent commits */ }
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
