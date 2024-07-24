import React from 'react';
import {getCategories, ICategory} from "../api/categories";
import {getHistory, ICommits} from "../api/history";
import Paper from "@mui/material/Paper";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';

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
                    <TableCell component="th" scope="row">Commit-ID</TableCell>
                    <TableCell>Atomic-ID</TableCell>
                    <TableCell>Action</TableCell>
                </TableRow>
                </TableHead>
                <TableBody>
                {commits.map(commit => (
                    <React.Fragment key={commit.id}>
                        <TableRow>
                            <TableCell>{commit.id}</TableCell>
                            <TableCell>{commit.time}</TableCell>
                            <TableCell>{commit.name}</TableCell>
                        </TableRow>
                        {
                            commit.atomics.map(atomic => (
                                <TableRow key={atomic.id}>
                                    <TableCell></TableCell>
                                    <TableCell>{atomic.id}</TableCell>
                                    <TableCell>{atomic.action}</TableCell>
                                </TableRow>
                            ))
                        }
                    </React.Fragment>
                ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
}

export default HistoryPage;
