import React from 'react';
import './HistoryTable.css';
import {ICommits} from "../../api/history";
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

function BuildRow(props: { commit: ICommits, isFirstCommit: boolean}) {
    const { commit, isFirstCommit} = props;
    const [isOpen, setIsOpen] = React.useState(false);

    const event_time = new Date(commit.time * 1000).toLocaleString();

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
                <TableCell className={ isFirstCommit ? "graph" : "graph verticalLine"}><div className="commit"></div></TableCell>
                <TableCell />
                <TableCell>{commit.id}</TableCell>
                <TableCell>{event_time}</TableCell>
                <TableCell>{commit.user}</TableCell>
                <TableCell>{commit.description}</TableCell>
            </TableRow>
            {
                isOpen ? commit.atomics.map((atomic, idx, items) => {
                    const isFirstAtomic = idx === 0;
                    const isLastAtomic = idx === items.length-1;
                    const atomicTime = new Date(atomic.timestamp * 1000).toLocaleString();
                    return (
                        <TableRow key={atomic.id}>
                            <TableCell />
                            <TableCell className="graph verticalLine" />
                            <TableCell className={
                                "graph" + (isFirstAtomic ? " closing" : "") + (isLastAtomic ? " opening" : "")
                            } >
                                <div className="commit atomic" />
                                {isFirstAtomic ? (<></>) : (<div className="verticalLine"/>) }
                            </TableCell>
                            <TableCell>{atomic.id}</TableCell>
                            <TableCell>{atomicTime}</TableCell>
                            <TableCell>{atomic.user}</TableCell>
                            <TableCell>{atomic.description}</TableCell>
                        </TableRow>
                    )
                }) : <></>
            }
        </React.Fragment>
    )
}

function HistoryTable(props: { commits: ICommits[] }) {
    const { commits } = props;

    // make sure the top value is the newest
    const sorted = React.useMemo(() => {
        return commits.sort((a, b) => b.time - a.time);
    }, [commits]);

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
                    {sorted.map((commit, idx) => (
                        <BuildRow key={commit.id} commit={commit} isFirstCommit={idx === 0} />
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    )
}

export default HistoryTable;
