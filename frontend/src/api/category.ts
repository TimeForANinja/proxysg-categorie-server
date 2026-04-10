import {ICategory, IMutableCategory} from "../model/types/category";

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

export const updateCategory = async (branch: string, id: string, updatedCategory: IMutableCategory): Promise<ICategory> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}`, {
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

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
};

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

export const addSubCategory = async (branch: string, cat_id: string, subCategoryId: string): Promise<void> => {
    const response = await fetch(`${getBaseUrl(branch)}/${cat_id}/category/${subCategoryId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to add sub-category ${subCategoryId} to category with id: ${cat_id}`);
    }

    const data = await response.json();
    if (data.status === "failed") {
        throw new Error(data.message);
    }
}

export const deleteSubCategory = async (branch: string, cat_id: string, subCategoryId: string): Promise<void> => {
    const response = await fetch(`${getBaseUrl(branch)}/${cat_id}/category/${subCategoryId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to remove sub-category ${subCategoryId} from category with id: ${cat_id}`);
    }

    const data = await response.json();
    if (data.status === "failed") {
        throw new Error(data.message);
    }
}

export const setSubCategory = async (branch: string, cat_id: string, subCategories: string[]): Promise<string[]> => {
    const response = await fetch(`${getBaseUrl(branch)}/${cat_id}/category`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ categories: subCategories }),
    });

    if (!response.ok) {
        throw new Error(`Failed to set sub-categories ${subCategories.join(',')} for category with id: ${cat_id}`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
}
