import React from 'react';
import Paper from "@mui/material/Paper";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import {IRestCommit} from "../../types/history";
import {formatUnixTimestamp} from "../../util/DateString";

interface HistoryTableProps {
    commits: IRestCommit[],
}

function HistoryTable(props: HistoryTableProps) {
    const { commits } = props;

    return (
        <TableContainer component={Paper} sx={{ maxHeight: 'calc(100vh - 160px)' }}>
            <Table
                sx={{ minWidth: 650 }}
                size="small"
                stickyHeader
            >
                <TableHead>
                    <TableRow>
                        <TableCell component="th" scope="row">Commit-ID</TableCell>
                        <TableCell>Time</TableCell>
                        <TableCell>User</TableCell>
                        <TableCell>Description</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {commits.map((commit) => (
                        <TableRow key={commit.uuid}>
                            <TableCell sx={{ fontFamily: 'monospace' }}>
                                {commit.uuid.substring(0, 8)}
                            </TableCell>
                            <TableCell>
                                {formatUnixTimestamp(commit.created_at)}
                            </TableCell>
                            <TableCell>{commit.author}</TableCell>
                            <TableCell>{commit.description}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    )
}

export default HistoryTable;
