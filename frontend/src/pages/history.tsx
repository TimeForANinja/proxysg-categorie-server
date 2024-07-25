import React from 'react';
import {getHistory, ICommits} from "../api/history";
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

function BuildRow(props: { commit: ICommits}) {
    const { commit} = props;
    const [isOpen, setIsOpen] = React.useState(false);

    return (
        <React.Fragment key={commit.id}>
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
                <TableCell>{commit.id}</TableCell>
                <TableCell>{commit.time}</TableCell>
                <TableCell>{commit.name}</TableCell>
            </TableRow>
            {
                isOpen ? commit.atomics.map(atomic => (
                    <TableRow key={atomic.id}>
                        <TableCell />
                        <TableCell />
                        <TableCell>{atomic.id}</TableCell>
                        <TableCell>{atomic.action}</TableCell>
                    </TableRow>
                )) : <></>
            }
        </React.Fragment>
    )
}

function HistoryPage() {
    const [commits, setCommits] = React.useState<ICommits[]>([]);

    React.useEffect(() => {
        Promise.all([ getHistory(0)])
            .then(([commitData]) => {
                setCommits(commitData);
            })
            .catch((error) => console.error("Error:", error));
    }, []);

    return (
        <TableContainer component={Paper}>
            <Table>
                <TableHead>
                <TableRow>
                    <TableCell />
                    <TableCell component="th" scope="row">Commit-ID</TableCell>
                    <TableCell>Atomic-ID</TableCell>
                    <TableCell>Action</TableCell>
                </TableRow>
                </TableHead>
                <TableBody>
                {commits.map(commit => (
                    <BuildRow key={commit.id} commit={commit}></BuildRow>
                ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
}

export default HistoryPage;
