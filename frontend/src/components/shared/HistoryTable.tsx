import React from 'react';
import './HistoryTable.css';
import Paper from "@mui/material/Paper";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import IconButton from "@mui/material/IconButton";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import {ICommit} from "../../types/history";


interface BuildRowProps {
    commit: ICommit,
    isFirstCommit: boolean,
}
function BuildRow(props: BuildRowProps) {
    const {commit, isFirstCommit} = props;
    const [isOpen, setIsOpen] = React.useState(false);

    return (
        <React.Fragment>
            <TableRow>
                <TableCell>
                    <IconButton
                        aria-label="expand row"
                        size="small"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        {isOpen ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                </TableCell>
                <TableCell className={ isFirstCommit ? "graph" : "graph verticalLine"}><div className="commit"></div></TableCell>
                <TableCell />
                <TableCell>{commit.description}</TableCell>
            </TableRow>
        </React.Fragment>
    )
}


interface HistoryTableProps {
    commits: ICommit[],
}
function HistoryTable(props: HistoryTableProps) {
    const { commits } = props;

    return (
        <TableContainer component={Paper}>
            <Table sx={{ minWidth: 650 }} size="small">
                <TableHead>
                    <TableRow>
                        <TableCell />
                        <TableCell />
                        <TableCell />
                        <TableCell component="th" scope="row">Commit-ID</TableCell>
                        <TableCell>Time</TableCell>
                        <TableCell>User</TableCell>
                        <TableCell>Description</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {commits.map((commit, idx) => (
                        <BuildRow
                            key={idx}
                            commit={commit}
                            isFirstCommit={idx === 0}
                            {...props}
                        />
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    )
}

export default HistoryTable;
