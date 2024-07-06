import React from 'react';
import {getAPITokens, IApiToken} from "../api/tokens";
import {getCategories, ICategory} from "../api/categories";
import Select from "react-select";

function ApiTokenPage() {
    const [tokens, setTokens] = React.useState<IApiToken[]>([]);
    const [categories, setCategory] = React.useState<ICategory[]>([]);

    React.useEffect(() => {
        Promise.all([ getCategories(), getAPITokens()])
            .then(([categoryData, tokenData]) => {
                setTokens(tokenData);
                setCategory(categoryData)
            })
            .catch((error) => console.error("Error:", error));
    }, []);

    return (
        <div>
            ApiTokenPage
            <table>
                <thead>
                <tr>
                    <th>ID</th>
                    <th>Token</th>
                    <th>Categories</th>
                </tr>
                </thead>
                <tbody>
                {tokens.map(token => (
                    <tr key={token.id}>
                        <td>{token.id}</td>
                        <td>{token.id}</td>
                        <td>
                            <Select
                                defaultValue={categories.filter(category => token.categories.includes(category.id)).map(c => ({ value: c.id, label: c.name }))}
                                isMulti
                                options={categories.map(c => ({ value: c.id, label: c.name }))}
                            />
                        </td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
}

export default ApiTokenPage;
