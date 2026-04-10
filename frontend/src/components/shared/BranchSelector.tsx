import React, { useEffect, useState } from 'react';
import { FormControl, Select, MenuItem, IconButton, Tooltip, Box } from '@mui/material';
import LockIcon from '@mui/icons-material/Lock';
import LockOpenIcon from '@mui/icons-material/LockOpen';
import { useBranch } from '../../model/BranchContext';
import { getBranches } from '../../api/branch';

const BranchSelector = () => {
    const { currentBranch, setCurrentBranch, isLocked, setLocked } = useBranch();
    const [branches, setBranches] = useState<string[]>([]);

    const refreshBranches = () => {
        getBranches().then(data => {
            setBranches(data);
            if (data.length > 0 && !data.includes(currentBranch)) {
                setCurrentBranch(data[0]);
            }
        }).catch(err => console.error("Failed to load branches", err));
    };

    useEffect(() => {
        refreshBranches();
    }, []);

    return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FormControl size="small" variant="outlined" sx={{ minWidth: 120 }}>
                <Select
                    value={currentBranch}
                    onChange={(e) => setCurrentBranch(e.target.value as string)}
                    sx={{
                        color: 'white',
                        '.MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                        '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'white' },
                        '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: 'white' },
                        '.MuiSvgIcon-root': { color: 'white' }
                    }}
                >
                    {branches.map((branch) => (
                        <MenuItem key={branch} value={branch}>
                            {branch}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>
            <Tooltip title={isLocked ? "Unlock Branch" : "Lock Branch"}>
                <IconButton onClick={() => setLocked(!isLocked)} color="inherit" size="small">
                    {isLocked ? <LockIcon /> : <LockOpenIcon />}
                </IconButton>
            </Tooltip>
        </Box>
    );
};

export default BranchSelector;
