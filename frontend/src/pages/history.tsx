import React from 'react';
import {getCategories, ICategory} from "../api/categories";
import {getHistory, ICommits} from "../api/history";

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
        <div>
            HistoryPage
            <table>
                <thead>
                <tr>
                    <th>Commit-ID</th>
                    <th>Atomic-ID</th>
                    <th>Action</th>
                </tr>
                </thead>
                <tbody>
                {commits.map(commit => (
                    <React.Fragment key={commit.id}>
                        <tr>
                            <td>{commit.id}</td>
                            <td>{commit.time}</td>
                            <td>{commit.name}</td>
                        </tr>
                        {
                            commit.atomics.map(atomic => (
                                <tr key={atomic.id}>
                                    <td></td>
                                    <td>{atomic.id}</td>
                                    <td>{atomic.action}</td>
                                </tr>
                            ))
                        }
                    </React.Fragment>
                ))}
                </tbody>
            </table>
        </div>
    );
}

export default HistoryPage;
