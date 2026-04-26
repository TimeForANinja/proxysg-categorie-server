import React from 'react';
import {getHistory} from "../../api/history";
import HistoryTable from "../shared/HistoryTable";
import {useBranch} from "../../hooks/useBranch";
import {IRestCommit} from "../../types/history";
import {useAuth} from "../../hooks/useLogin";
import {Box, Button, TextField, Card, CardContent, Typography, Divider, Stack, Dialog, DialogTitle, DialogContent, DialogActions} from "@mui/material";
import {doCommit, revertBranch} from "../../api/branch";
import {useNotification} from "../../hooks/useNotification";
import CommitCompareModal from "./CommitCompareModal";

function HistoryPage() {
    const authMgmt = useAuth();
    const { currentBranch, isLocked } = useBranch();
    const { showError, showSuccess } = useNotification();

    const [commits, setCommits] = React.useState<IRestCommit[]>([]);
    const [selectedCommits, setSelectedCommits] = React.useState<string[]>([]);
    const [isCompareOpen, setIsCompareOpen] = React.useState(false);

    const [revertTarget, setRevertTarget] = React.useState<IRestCommit | null>(null);

    // State for the commit message
    const [commitMessage, setCommitMessage] = React.useState<string>("");

    const fetchData = React.useCallback(() => {
        getHistory(authMgmt.token, currentBranch)
            .then((commitData) => {
                // save history to state
                setCommits(commitData);
            })
            .catch((error) => showError(error.message));
    }, [currentBranch, authMgmt.token, showError]);

    React.useEffect(() => {
        fetchData();
    }, [fetchData]);

    const onCommit = async () => {
        if (!commitMessage.trim()) {
            showError("Please enter a commit message");
            return;
        }
        try {
            await doCommit(authMgmt.token, commitMessage);
            showSuccess("Changes committed successfully");
            setCommitMessage(""); // Clear the commit message after submission
            fetchData();
        } catch (e: any) {
            showError(e.message);
        }
    };

    const handleRevert = async () => {
        if (!revertTarget) return;
        try {
            await revertBranch(authMgmt.token, revertTarget.uuid);
            showSuccess(`Successfully reverted to commit ${revertTarget.uuid.substring(0, 8)}`);
            setRevertTarget(null);
            fetchData();
        } catch (e: any) {
            showError(e.message);
        }
    };

    const onSelectCommit = (uuid: string) => {
        setSelectedCommits(prev => {
            if (prev.includes(uuid)) {
                return prev.filter(id => id !== uuid);
            }
            if (prev.length >= 2) return prev;
            return [...prev, uuid];
        });
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
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        Recent Commits
                        <Typography variant="body2" component="span" color="text.secondary">
                            ({commits.length})
                        </Typography>
                    </Typography>
                    <Button
                        variant="outlined"
                        disabled={selectedCommits.length !== 2}
                        onClick={() => setIsCompareOpen(true)}
                    >
                        Compare Selected ({selectedCommits.length}/2)
                    </Button>
                </Box>
                <Divider sx={{ mb: 2 }} />
                <Card variant="outlined">
                    <HistoryTable
                        commits={commits}
                        onRevert={setRevertTarget}
                        selectedCommits={selectedCommits}
                        onSelectCommit={onSelectCommit}
                        isLocked={isLocked}
                    />
                </Card>
            </Box>

            {/* Revert Confirmation Dialog */}
            <Dialog open={!!revertTarget} onClose={() => setRevertTarget(null)}>
                <DialogTitle>Confirm Revert</DialogTitle>
                <DialogContent>
                    <Typography>
                        Are you sure you want to revert the current branch to the state of commit <b>{revertTarget?.uuid.substring(0, 8)}</b>?
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        This will overwrite any uncommitted changes in your branch.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setRevertTarget(null)}>Cancel</Button>
                    <Button onClick={handleRevert} color="error" variant="contained">Revert</Button>
                </DialogActions>
            </Dialog>

            {/* Compare Modal */}
            {isCompareOpen && (
                <CommitCompareModal
                    open={isCompareOpen}
                    onClose={() => setIsCompareOpen(false)}
                    commitUuids={selectedCommits}
                    allCommits={commits}
                />
            )}
        </Stack>
    );
}

export default HistoryPage;
