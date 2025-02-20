export interface ICategory {
    id: number;
    name: string;
    color: number;
    description: string;
}

export const getCategories = async (): Promise<ICategory[]> => {
    const response = await fetch('http://127.0.0.1:3080/api/categories');
    const data = await response.json();
    return data.data;
}

export const updateCategory = async (updatedCategory: ICategory): Promise<ICategory> => {
    const response = await fetch(`http://127.0.0.1:3080/api/categories/${updatedCategory.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedCategory),
    });

    if (!response.ok) {
        throw new Error(`Failed to update category with id: ${updatedCategory.id}`);
    }

    const data = await response.json();
    return data.data;
};

export const createCategory = async (partialCategory: ICategory): Promise<ICategory> => {
    const response = await fetch(`http://127.0.0.1:3080/api/categories`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(partialCategory),
    });

    if (!response.ok) {
        throw new Error(`Failed to create category.`);
    }

    const data = await response.json();
    return data.data;
};


export const deleteCategory = async (category: ICategory): Promise<ICategory> => {
    const response = await fetch(`http://127.0.0.1:3080/api/categories/${category.id}`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        throw new Error(`Failed to delete category.`);
    }

    const data = await response.json();
    return data.data;
};
