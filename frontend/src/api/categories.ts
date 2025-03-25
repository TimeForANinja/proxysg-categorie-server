export interface IMutableCategory {
    name: string;
    color: number;
    description: string;
}

export interface ICategory extends IMutableCategory {
    id: number;
}

export const getCategories = async (): Promise<ICategory[]> => {
    const response = await fetch('/api/category');
    const data = await response.json();
    return data.data;
}

export const updateCategory = async (id: Number, updatedCategory: IMutableCategory): Promise<ICategory> => {
    const response = await fetch(`/api/category/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedCategory),
    });

    if (!response.ok) {
        throw new Error(`Failed to update category with id: ${id}`);
    }

    const data = await response.json();
    return data.data;
};

export const createCategory = async (partialCategory: IMutableCategory): Promise<ICategory> => {
    const response = await fetch(`/api/category`, {
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

export const deleteCategory = async (id: number): Promise<void> => {
    const response = await fetch(`/api/category/${id}`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        throw new Error(`Failed to delete category.`);
    }
};
