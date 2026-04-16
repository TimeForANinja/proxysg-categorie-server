import {ICategory, ICategoryInput, ICategoryOutput, IListCategoryOutput} from "../types/category";
import {GenericOutput} from "../types/api";

const getBaseUrl = (branch: string) => `/api/branch/${branch}/category`;

export const getCategories = async (userToken: string, branch: string): Promise<ICategory[]> => {
    const response = await fetch(getBaseUrl(branch), {
        headers: { 'jwt-token': userToken },
    });
    const data: IListCategoryOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to get category list`);
    }

    return data.data;
}

export const createCategory = async (userToken: string, branch: string, category: ICategoryInput): Promise<ICategory> => {
    const response = await fetch(getBaseUrl(branch), {
        method: 'POST',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(category),
    });

    const data: ICategoryOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to create category.`);
    }

    return data.data;
};

export const deleteCategory = async (userToken: string, branch: string, id: string): Promise<GenericOutput> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}`, {
        method: 'DELETE',
        headers: { 'jwt-token': userToken },
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to delete category.`);
    }

    return data;
};

export const updateCategory = async (userToken: string, branch: string, id: string, category: ICategoryInput): Promise<ICategory> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}`, {
        method: 'PUT',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(category),
    });

    const data: ICategoryOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to update category.`);
    }

    return data.data;
};
