import React from 'react';
import Paper from "@mui/material/Paper";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import {IRestCommit} from "../../types/history";
import {formatUnixTimestamp, formatUnixDateOnly} from "../../util/DateString";
import {short_uuid} from "../../util/uuid";

import {IconButton, Tooltip, Checkbox} from "@mui/material";
import {Restore as RestoreIcon} from "@mui/icons-material";

interface HistoryTableProps {
    commits: IRestCommit[],
    small?: boolean,
    onRevert?: (commit: IRestCommit) => void,
    selectedCommits?: string[],
    onSelectCommit?: (commitUuid: string) => void,
    isLocked?: boolean,
}

function HistoryTable({ commits, small, onRevert, selectedCommits, onSelectCommit, isLocked }: HistoryTableProps) {
    return (
        <TableContainer component={Paper} sx={{ maxHeight: 'calc(100vh - 160px)' }}>
            <Table
                sx={{ minWidth: small ? 300 : 650, '& .MuiTableCell-root': { fontFamily: 'monospace' } }}
                size="small"
                stickyHeader
            >
                <TableHead>
                    <TableRow>
                        {!small && onSelectCommit && <TableCell padding="checkbox" />}
                        {!small && <TableCell>Commit-ID</TableCell>}
                        <TableCell>Time</TableCell>
                        <TableCell>User</TableCell>
                        <TableCell>Description</TableCell>
                        {!small && onRevert && !isLocked && <TableCell align="right">Actions</TableCell>}
                    </TableRow>
                </TableHead>
                <TableBody>
                    {commits.map((commit) => (
                        <TableRow
                            key={commit.uuid}
                            hover
                            selected={selectedCommits?.includes(commit.uuid)}
                        >
                            {!small && onSelectCommit && (
                                <TableCell padding="checkbox">
                                    <Checkbox
                                        checked={selectedCommits?.includes(commit.uuid)}
                                        onChange={() => onSelectCommit(commit.uuid)}
                                        disabled={!selectedCommits?.includes(commit.uuid) && selectedCommits && selectedCommits.length >= 2}
                                    />
                                </TableCell>
                            )}
                            {!small && (
                                <TableCell sx={{ fontFamily: 'monospace' }}>
                                    {short_uuid(commit.uuid)}
                                </TableCell>
                            )}
                            <TableCell>
                                {small ? formatUnixDateOnly(commit.created_at) : formatUnixTimestamp(commit.created_at)}
                            </TableCell>
                            <TableCell>{commit.author}</TableCell>
                            <TableCell>{commit.description}</TableCell>
                            {!small && onRevert && !isLocked && (
                                <TableCell align="right">
                                    <Tooltip title="Revert to this commit">
                                        <IconButton
                                            size="small"
                                            onClick={() => onRevert(commit)}
                                            color="primary"
                                        >
                                            <RestoreIcon />
                                        </IconButton>
                                    </Tooltip>
                                </TableCell>
                            )}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
}

export default HistoryTable;
