import React from 'react';
import { FormControl, Select, MenuItem, Box, Divider, Typography } from '@mui/material';
import LockIcon from '@mui/icons-material/Lock';
import LockOpenIcon from '@mui/icons-material/LockOpen';
import {DEFAULT_BRANCH, useBranch} from '../../hooks/useBranch';
import { useNotification } from '../../hooks/useNotification';
import { getBranches } from '../../api/branch';
import { IRestBranchInfo } from '../../types/branch';
import {useAuth} from "../../hooks/useLogin";

const RO_VALUE = 'ro';

const sort_branches = (list: IRestBranchInfo[]): IRestBranchInfo[] => {
    return list.sort((a, b) => {
        // default should always be first
        if (a.name == DEFAULT_BRANCH) {
            return -1;
        } else if (b.name == DEFAULT_BRANCH) {
            return 1;
        }
        // next should be the user branch, identified by not being ro
        if (a.permission !== RO_VALUE) {
            return -1;
        } else if (b.permission !== RO_VALUE) {
            return 1;
        }
        // lastly, sort alphabetically
        return a.name.localeCompare(b.name);
    });
};

const BranchSelector = () => {
    const authMgmt = useAuth();
    const { showError } = useNotification();
    const { currentBranch, setCurrentBranch, isLocked, setIsLocked } = useBranch();

    const [branches, setBranches] = React.useState<IRestBranchInfo[]>([]);

    React.useEffect(() => {
        getBranches(authMgmt.token).then(data => {
            setBranches(data);
            if (data.length > 0) {
                const names = data.map(b => b.name);
                if (!names.includes(currentBranch)) {
                    setCurrentBranch(data[0].name);
                }
            }
        }).catch(err => showError(err.message || "Failed to load branches"));
    }, [authMgmt.token, currentBranch, setCurrentBranch, showError]);

    React.useEffect(() => {
        const branchInfo = branches.find(b => b.name === currentBranch);
        if (branchInfo) {
            setIsLocked(branchInfo.permission === RO_VALUE);
        }
    }, [currentBranch, branches, setIsLocked]);

    const sortedBranches = React.useMemo(() => sort_branches(branches), [branches]);

    const activeColor = isLocked ? '#ff1744' : 'white';

    return (
        <Box sx={{
            display: 'flex',
            alignItems: 'stretch',
            border: `1px solid ${isLocked ? 'rgba(255, 23, 68, 0.5)' : 'rgba(255, 255, 255, 0.5)'}`,
            borderRadius: 1,
            overflow: 'hidden',
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            '&:hover': {
                borderColor: activeColor
            },
            transition: 'border-color 0.2s'
        }}>
            <FormControl size="small" variant="standard" sx={{ minWidth: 150 }}>
                <Select
                    value={currentBranch}
                    onChange={(e) => setCurrentBranch(e.target.value as string)}
                    disableUnderline
                    sx={{
                        color: activeColor,
                        px: 1,
                        '.MuiSelect-select': {
                            py: 0.5,
                            display: 'flex',
                            alignItems: 'center'
                        },
                        '.MuiSvgIcon-root': { color: activeColor }
                    }}
                >
                    {sortedBranches.map((branch) => (
                        <MenuItem key={branch.name} value={branch.name}>
                            <Typography variant="body2" sx={{ color: branch.permission === RO_VALUE ? '#ff1744' : 'inherit' }}>
                                {branch.name}
                            </Typography>
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>
            <Divider orientation="vertical" flexItem sx={{ borderColor: isLocked ? 'rgba(255, 23, 68, 0.3)' : 'rgba(255, 255, 255, 0.3)' }} />
            <Box sx={{
                width: '40px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: activeColor,
                flexShrink: 0
            }}>
                {isLocked ? <LockIcon fontSize="small" /> : <LockOpenIcon fontSize="small" />}
            </Box>
        </Box>
    );
};

export default BranchSelector;
