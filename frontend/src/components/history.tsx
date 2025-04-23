import React from 'react';
import {getHistory, ICommits} from "../api/history";
import {useAuth} from "../model/AuthContext";
import HistoryTable from "./shared/HistoryTable";

function HistoryPage() {
    const authMgmt = useAuth();
    const [commits, setCommits] = React.useState<ICommits[]>([]);

    React.useEffect(() => {
        Promise.all([getHistory(authMgmt.token)])
            .then(([commitData]) => {
                // save history to state
                setCommits(commitData);
            })
            .catch((error) => console.error("Error:", error));
    }, [authMgmt]);

    return (
        <HistoryTable
            commits={commits}
        />
    );
}

export default HistoryPage;
