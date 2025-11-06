import React from 'react';
import './HistoryTable.css';
import {ICommits, IReferred} from "../../api/history";
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
import Button from "@mui/material/Button";
import useSlidingWindow from "../../hooks/useSlidingWindow";

interface filterParams {
    url?: string,
    token?: string,
    category?: string,
}
/**
 * Utility method to filter out irrelevant entries from the history table.
 * @param x - the entry to check
 * @param props - the filter parameters
 */
const filterRelevant = (x: IReferred, props: filterParams) => {
    if (props.url && !x.ref_url.includes(props.url)) return false;
    else if (props.token && !x.ref_token.includes(props.token)) return false;
    else if (props.category && !x.ref_category.includes(props.category)) return false;
    return true;
}


interface BuildRowProps extends filterParams {
    commit: ICommits,
    isFirstCommit: boolean,
    isLastCommit: boolean,
}
function BuildRow(props: BuildRowProps) {
    const {commit, isFirstCommit, isLastCommit} = props;
    const [isOpen, setIsOpen] = React.useState(false);
    const event_time = new Date(commit.time * 1000).toLocaleString();

    // pagination window for atomics within a commit (offloaded to reusable hook)
    const filteredAtomics = React.useMemo(() => commit.atomics.filter(a => filterRelevant(a, props)), [commit.atomics, props]);
    const { startIndex, endIndex, topHidden, bottomHidden, showMoreTop, showMoreBottom } = useSlidingWindow(filteredAtomics.length, {
        resetKeys: [filteredAtomics],
    });
    const visibleItems = filteredAtomics.slice(startIndex, endIndex);

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
                /**
                 * Render the atomic changes as a list if the parent commit is "open".
                 * At the Top and Bottom we have (opt) Buttons for Pagination.
                 * The first and last visible atomic changes are special, since the have "curved" lines to visually connect to the commit.
                 */
                isOpen ? (
                    <>
                        {topHidden > 0 && (
                            <TableRow>
                                <TableCell />
                                <TableCell className="graph verticalLine" />
                                <TableCell className="graph" />
                                <TableCell colSpan={4}>
                                    <Button size="small" onClick={showMoreTop}>
                                        {topHidden} hidden, click to show {Math.min(100, topHidden)} more (slide window)
                                    </Button>
                                </TableCell>
                            </TableRow>
                        )}
                        {visibleItems.map((atomic, idx) => {
                            const isFirstAtomic = (startIndex === 0) && (idx === 0);
                            const isLastAtomic = (endIndex === filteredAtomics.length) && (idx === visibleItems.length - 1);
                            const atomicTime = new Date(atomic.timestamp * 1000).toLocaleString();
                            return (
                                <TableRow key={atomic.id}>
                                    <TableCell />
                                    <TableCell className="graph verticalLine" />
                                    <TableCell className={
                                        "graph" + (isFirstAtomic ? " closing" : "") + ((isLastAtomic && !isLastCommit) ? " opening" : "")
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
                        })}
                        {bottomHidden > 0 && (
                            <TableRow>
                                <TableCell />
                                <TableCell className="graph verticalLine" />
                                <TableCell className="graph">
                                    <div className="verticalLine"/>
                                </TableCell>
                                <TableCell colSpan={4}>
                                    <Button size="small" onClick={showMoreBottom}>
                                        {bottomHidden} hidden, click to show {Math.min(100, bottomHidden)} more (slide window)
                                    </Button>
                                </TableCell>
                            </TableRow>
                        )}
                    </>
                ) : <></>
            }
        </React.Fragment>
    )
}


interface HistoryTableProps extends filterParams {
    commits: ICommits[],
}
function HistoryTable(props: HistoryTableProps) {
    const { commits } = props;

    // make sure the top value is the newest
    const sorted = React.useMemo(() => {
        return commits.filter(c => filterRelevant(c, props)).sort((a, b) => b.time - a.time);
    }, [commits, props]);

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
                        <BuildRow
                            key={commit.id}
                            commit={commit}
                            isFirstCommit={idx === 0}
                            isLastCommit={idx === sorted.length-1}
                            {...props}
                        />
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    )
}

export default HistoryTable;
