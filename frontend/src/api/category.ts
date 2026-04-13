import {ICategory, ICategoryInput, ICategoryOutput, IListCategoryOutput} from "../types/category";
import {GenericOutput} from "../types/api";

const getBaseUrl = (branch: string) => `/api/branch/${branch}/category`;

export const getCategories = async (branch: string): Promise<ICategory[]> => {
    const response = await fetch(getBaseUrl(branch));
    const data: IListCategoryOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to get category list`);
    }

    return data.data;
}

export const createCategory = async (branch: string, category: ICategoryInput): Promise<ICategory> => {
    const response = await fetch(getBaseUrl(branch), {
        method: 'POST',
        headers: {
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

export const deleteCategory = async (branch: string, id: string): Promise<GenericOutput> => {
    const response = await fetch(`${getBaseUrl(branch)}/${id}`, {
        method: 'DELETE',
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to delete category.`);
    }

    return data;
};
