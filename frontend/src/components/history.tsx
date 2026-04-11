import React from 'react';
import Grid from "@mui/material/Grid2";

import {getHistory} from "../api/history";
import HistoryTable from "./shared/HistoryTable";
import {useBranch} from "../hooks/useBranch";
import {ICommit} from "../types/history";

function HistoryPage() {
    const { currentBranch } = useBranch();
    const [commits, setCommits] = React.useState<ICommit[]>([]);

    React.useEffect(() => {
        getHistory(currentBranch)
            .then((commitData) => {
                // save history to state
                setCommits(commitData);
            })
            .catch((error) => console.error("Error:", error));
    }, [currentBranch]);

    return (
        <>
            <Grid
                container
                spacing={1}
                justifyContent="center"
                alignItems="center"
            >
                <Grid size={12}>
                    <HistoryTable
                        commits={commits}
                    />
                </Grid>
            </Grid>
        </>
    );
}

export default HistoryPage;
