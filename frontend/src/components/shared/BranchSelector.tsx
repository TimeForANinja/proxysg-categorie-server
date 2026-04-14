import React, { useEffect, useState } from 'react';
import { FormControl, Select, MenuItem, Box, Divider, Typography } from '@mui/material';
import LockIcon from '@mui/icons-material/Lock';
import LockOpenIcon from '@mui/icons-material/LockOpen';
import { useBranch } from '../../hooks/useBranch';
import { getBranches } from '../../api/branch';
import { IRestBranchInfo } from '../../types/branch';

const RO_VALUE = 'ro'

const BranchSelector = () => {
    const { currentBranch, setCurrentBranch, isLocked, setIsLocked } = useBranch();
    const [branches, setBranches] = useState<IRestBranchInfo[]>([]);

    const refreshBranches = () => {
        getBranches().then(data => {
            setBranches(data);
            if (data.length > 0) {
                const names = data.map(b => b.name);
                if (!names.includes(currentBranch)) {
                    setCurrentBranch(data[0].name);
                }
            }
        }).catch(err => console.error("Failed to load branches", err));
    };

    useEffect(() => {
        refreshBranches();
    }, []);

    useEffect(() => {
        const branchInfo = branches.find(b => b.name === currentBranch);
        if (branchInfo) {
            setIsLocked(branchInfo.permission === RO_VALUE);
        }
    }, [currentBranch, branches, setIsLocked]);

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
                    {branches.map((branch) => (
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
