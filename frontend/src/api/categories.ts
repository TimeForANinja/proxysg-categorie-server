import {ICategory, IMutableCategory} from "../model/types/category";

export const getCategories = async (userToken: string): Promise<ICategory[]> => {
    const response = await fetch('/api/category', {
        headers: { 'jwt-token': userToken },
    });

    if (!response.ok) {
        throw new Error(`Failed to get category list`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
}

export const updateCategory = async (userToken: string, id: string, updatedCategory: IMutableCategory): Promise<ICategory> => {
    const response = await fetch(`/api/category/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
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

export const createCategory = async (userToken: string, partialCategory: IMutableCategory): Promise<ICategory> => {
    const response = await fetch(`/api/category`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
        },
        body: JSON.stringify(partialCategory),
    });

    if (!response.ok) {
        throw new Error(`Failed to create category.`);
    }

    const data = await response.json();
    return data.data;
};

export const deleteCategory = async (userToken: string, id: string): Promise<void> => {
    const response = await fetch(`/api/category/${id}`, {
        method: 'DELETE',
        headers: { 'jwt-token': userToken },
    });

    if (!response.ok) {
        throw new Error(`Failed to delete category.`);
    }
};

export const addSubCategory = async (userToken: string, cat_id: string, subCategoryId: string): Promise<void> => {
    const response = await fetch(`/api/category/${cat_id}/category/${subCategoryId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
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

export const deleteSubCategory = async (userToken: string, cat_id: string, subCategoryId: string): Promise<void> => {
    const response = await fetch(`/api/category/${cat_id}/category/${subCategoryId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
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

export const setSubCategory = async (userToken: string, cat_id: string, subCategories: string[]): Promise<string[]> => {
    const response = await fetch(`/api/category/${cat_id}/category`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
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
