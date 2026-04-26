import React, {useMemo} from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Box,
    Typography,
    CircularProgress,
    Divider,
} from '@mui/material';
import {renderCommit} from "../../api/history";
import {useAuth} from "../../hooks/useLogin";
import {useNotification} from "../../hooks/useNotification";
import {IRestCommit} from "../../types/history";
import {short_uuid} from "../../util/uuid";
import {formatUnixTimestamp} from "../../util/DateString";
import {buildDiff, AlignedDiffLine} from "../../util/build_diff";

interface CommitCompareModalProps {
    open: boolean;
    onClose: () => void;
    commitUuids: string[];
    allCommits: IRestCommit[];
}

const CommitCompareModal: React.FC<CommitCompareModalProps> = ({ open, onClose, commitUuids, allCommits }) => {
    const authMgmt = useAuth();
    const { showError } = useNotification();
    const [loading, setLoading] = React.useState(true);
    const [renders, setRenders] = React.useState<string[]>([]);

    const sortedUuids = useMemo(() => {
        return [...commitUuids].sort((a, b) => {
            const ca = allCommits.find(c => c.uuid === a)?.created_at || 0;
            const cb = allCommits.find(c => c.uuid === b)?.created_at || 0;
            return ca - cb;
        });
    }, [commitUuids, allCommits]);

    React.useEffect(() => {
        if (open && sortedUuids.length === 2) {
            setLoading(true);
            
            Promise.all(sortedUuids.map(uuid => renderCommit(authMgmt.token, uuid)))
                .then((fetchedRenders) => {
                    setRenders(fetchedRenders);
                    setLoading(false);
                })
                .catch(err => {
                    showError(err.message || "Failed to fetch commit details");
                    setLoading(false);
                    onClose();
                });
        }
    }, [open, sortedUuids, authMgmt.token, showError, onClose]);

    const diffLines = useMemo(() => {
        if (renders.length !== 2) return [];
        return buildDiff(renders[0], renders[1]);
    }, [renders]);

    const getCommitInfo = (uuid: string) => {
        return allCommits.find(c => c.uuid === uuid);
    };

    const getLineColor = (type: AlignedDiffLine['type']) => {
        switch (type) {
            case 'added': return '#e6ffed';
            case 'removed': return '#ffeef0';
            case 'modified': return '#fff5b1';
            case 'spacer': return '#f6f8fa';
            default: return 'inherit';
        }
    };

    return (
        <Dialog 
            open={open} 
            onClose={onClose} 
            maxWidth="xl" 
            fullWidth
            scroll="paper"
        >
            <DialogTitle>
                Compare Commits
            </DialogTitle>
            <DialogContent dividers sx={{ p: 0 }}>
                {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                        <CircularProgress />
                    </Box>
                ) : (
                    <Box>
                        <Box sx={{ position: 'sticky', top: 0, zIndex: 10, bgcolor: 'background.paper' }}>
                            <Box sx={{ display: 'flex', p: 2, bgcolor: 'grey.50' }}>
                                {sortedUuids.map((uuid, idx) => {
                                    const commit = getCommitInfo(uuid);
                                    return (
                                        <Box key={uuid} sx={{ flex: 1, px: 2 }}>
                                            <Typography variant="subtitle2">
                                                <b>{idx === 0 ? "Original" : "New"}:</b> {short_uuid(uuid)}
                                            </Typography>
                                            <Typography variant="caption" sx={{ display: 'block' }} color="text.secondary">
                                                <b>Date:</b> {commit ? formatUnixTimestamp(commit.created_at) : 'unknown'}
                                            </Typography>
                                            <Typography variant="caption" sx={{ display: 'block' }} color="text.secondary">
                                                <b>Author:</b> {commit?.author}
                                            </Typography>
                                            <Typography variant="caption" sx={{ display: 'block' }} color="text.secondary" noWrap title={commit?.description}>
                                                <b>Message:</b> {commit?.description}
                                            </Typography>
                                        </Box>
                                    );
                                })}
                            </Box>
                            <Divider />
                        </Box>
                        <Box 
                            sx={{ 
                                fontFamily: 'monospace', 
                                fontSize: '0.85rem',
                            }}
                        >
                            {diffLines.map((line, idx) => (
                                <Box 
                                    key={idx} 
                                    sx={{ 
                                        display: 'flex', 
                                        bgcolor: getLineColor(line.type),
                                        '&:hover': { bgcolor: line.type === 'unchanged' ? 'rgba(0,0,0,0.02)' : undefined },
                                        minHeight: '1.2rem',
                                        borderBottom: line.type === 'spacer' ? '1px dashed #ddd' : 'none'
                                    }}
                                >
                                    {line.type === 'spacer' ? (
                                        <Box sx={{ flex: 1, textAlign: 'center', color: 'text.secondary', py: 0.5 }}>...</Box>
                                    ) : (
                                        <>
                                            <Box sx={{ 
                                                flex: 1, 
                                                whiteSpace: 'pre-wrap', 
                                                wordBreak: 'break-all',
                                                px: 1, 
                                                borderRight: '1px solid #eee',
                                                color: line.type === 'added' ? 'transparent' : 'inherit',
                                            }}>
                                                {line.left || (line.type === 'added' ? "" : " ")}
                                            </Box>
                                            <Box sx={{ 
                                                flex: 1, 
                                                whiteSpace: 'pre-wrap', 
                                                wordBreak: 'break-all',
                                                px: 1,
                                                color: line.type === 'removed' ? 'transparent' : 'inherit',
                                            }}>
                                                {line.right || (line.type === 'removed' ? "" : " ")}
                                            </Box>
                                        </>
                                    )}
                                </Box>
                            ))}
                        </Box>
                    </Box>
                )}
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Close</Button>
            </DialogActions>
        </Dialog>
    );
};

export default CommitCompareModal;
