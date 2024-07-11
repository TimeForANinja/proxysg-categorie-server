import React from 'react';
import {getCategories, ICategory} from "../api/categories";
import {colors} from "../api/colormixer";

function CategoriesPage() {
    const [categories, setCategory] = React.useState<ICategory[]>([]);

    React.useEffect(() => {
        Promise.all([getCategories()])
            .then(([categoriesData]) => {
                setCategory(categoriesData);
            })
            .catch((error) => console.error("Error:", error));
    }, []);

    return (
        <div>
            CategoriesPage
            <table>
                <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Color</th>
                </tr>
                </thead>
                <tbody>
                {categories.map(category => (
                    <tr key={category.id}>
                        <td>{category.id}</td>
                        <td>{category.name}</td>
                        <td style={{
                            backgroundColor: colors[category.color],
                        }}>{colors[category.color]}</td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
}

export default CategoriesPage;
