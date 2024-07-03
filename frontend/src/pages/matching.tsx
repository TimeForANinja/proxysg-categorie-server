import React from 'react';
import Select from 'react-select';

interface IURL {
    id: number;
    hostname: string;
    memberOf: number[];
}

interface ICategory {
    value: number;
    label: string;
}

function MatchingListPage() {
    const [urls, setURLs] = React.useState<IURL[]>([]);
    const [categories, setCategory] = React.useState<ICategory[]>([]);
    const [expandedId, setExpandedId] = React.useState<number | null>(null);

    const handleExpand = (id: number) => {
        setExpandedId(prevId => prevId === id ? null : id);
    }

    React.useEffect(() => {
        const getURLs = async () => {
            const response = await fetch('/api/urls');
            const data = await response.json();
            return data;
        }

        const getCategories = async () => {
            const response = await fetch('/api/categories');
            const data = await response.json();
            return data;
        }

        Promise.all([getURLs(), getCategories()])
            .then(([urlsData, categoriesData]) => {
                setURLs(urlsData);
                setCategory(categoriesData);
            })
            .catch((error) => console.error("Error:", error));
    }, []);

    return (
        <table className="table" style={{width: '100%'}}>
            <thead>
            <tr>
                <th>ID</th>
                <th>Hostname</th>
                <th>Categories</th>
                <th>Details</th>
            </tr>
            </thead>
            <tbody>
            {urls.map(url => (
                <React.Fragment key={url.id}>
                    <tr key={url.id}>
                        <td>{url.id}</td>
                        <td>{url.hostname}</td>
                        <td>
                            <Select
                                defaultValue={categories.filter(category => url.memberOf.includes(category.value))}
                                isMulti
                                options={categories}
                            />
                        </td>
                        <td>
                            <button onClick={() => handleExpand(url.id)}>{"<"}</button>
                        </td>
                    </tr>
                    <tr key={url.id + '-expand'} style={{display: expandedId === url.id ? '' : 'none'}}>
                        <td colSpan={99}>Hello there</td>
                    </tr>
                </React.Fragment>
            ))}
            </tbody>
        </table>
    );
}

export default MatchingListPage;
