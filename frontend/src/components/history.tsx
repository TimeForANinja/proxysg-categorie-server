import React from 'react';
import {getHistory} from "../api/history";
import HistoryTable from "./shared/HistoryTable";
import {useBranch} from "../hooks/useBranch";
import {IRestCommit} from "../types/history";
import {useAuth} from "../hooks/useLogin";
import {Box, Button, TextField, Card, CardContent, Typography, Divider, Stack} from "@mui/material";
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
        <Stack spacing={4} sx={{ maxWidth: '1200px', margin: '0 auto', p: 2 }}>
            { /* Commit Section */ }
            {!isLocked && (
                <Card variant="outlined" sx={{ bgcolor: 'action.hover' }}>
                    <CardContent>
                        <Typography variant="h6" gutterBottom>
                            Commit Changes
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            Provide a descriptive message for your changes before committing them to the branch.
                        </Typography>
                        <Box sx={{ display: "flex", gap: 2, alignItems: "flex-start" }}>
                            <TextField
                                fullWidth
                                label="Commit Message"
                                placeholder="What did you change?"
                                variant="outlined"
                                value={commitMessage}
                                onChange={(e) => setCommitMessage(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                                        onCommit();
                                    }
                                }}
                                multiline
                                rows={2}
                            />
                            <Button
                                variant="contained"
                                onClick={() => onCommit()}
                                sx={{ height: '56px', minWidth: '120px' }}
                                disabled={!commitMessage.trim()}
                            >
                                Commit
                            </Button>
                        </Box>
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                            Tip: Press Ctrl+Enter to commit quickly.
                        </Typography>
                    </CardContent>
                </Card>
            )}

            { /* History Section */ }
            <Box>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    Recent Commits
                    <Typography variant="body2" component="span" color="text.secondary">
                        ({commits.length})
                    </Typography>
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Card variant="outlined">
                    <HistoryTable commits={commits} />
                </Card>
            </Box>
        </Stack>
    );
}

export default HistoryPage;
