import {
    ICategory, ICategoryCreateInput, ICategoryUpdateInput, ICategoryOutput, IListCategoryOutput,
    IListCategoryDetailsOutput, IRestCategoryDetail
} from "../types/category";
import {GenericOutput} from "../types/api";


export const getCategories = async (userToken: string, branch: string): Promise<IRestCategoryDetail[]> => {
    const response = await fetch(`/api/branch/${branch}/category`, {
        headers: { 'jwt-token': userToken },
    });
    const data: IListCategoryDetailsOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to get category list`);
    }

    return data.data;
}

export const createCategory = async (userToken: string, category: ICategoryCreateInput): Promise<ICategory> => {
    const response = await fetch('/api/branch/@me/category', {
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

export const deleteCategory = async (userToken: string, id: string): Promise<GenericOutput> => {
    const response = await fetch(`/api/branch/@me/category/${id}`, {
        method: 'DELETE',
        headers: { 'jwt-token': userToken },
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to delete category.`);
    }

    return data;
};

export const updateCategory = async (userToken: string, id: string, category: ICategoryUpdateInput): Promise<ICategory> => {
    const response = await fetch(`/api/branch/@me/category/${id}`, {
        method: 'PATCH',
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
