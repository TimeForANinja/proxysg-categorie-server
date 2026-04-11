import {ICategory, IMutableCategory} from "../types/category";

const getBaseUrl = (branch: string) => `/api/branch/${branch}/category`;

export const getCategories = async (branch: string): Promise<ICategory[]> => {
    const response = await fetch(getBaseUrl(branch));

    if (!response.ok) {
        throw new Error(`Failed to get category list`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
}

export const createCategory = async (branch: string, partialCategory: IMutableCategory): Promise<ICategory> => {
    const response = await fetch(getBaseUrl(branch), {
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

export const deleteCategory = async (branch: string, id: string): Promise<void> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        throw new Error(`Failed to delete category.`);
    }
};
