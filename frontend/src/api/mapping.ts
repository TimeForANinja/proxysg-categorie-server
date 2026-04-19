import {IURLCategoryMappingInput} from "../types/url";
import {GenericOutput} from "../types/api";

export const addURLCategory = async (userToken: string, categoryId: string, mapping: IURLCategoryMappingInput): Promise<GenericOutput> => {
    const response = await fetch(`/api/branch/@me/category/${categoryId}/url`, {
        method: 'POST',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(mapping),
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to add url ${mapping.url_id} to category ${categoryId}`);
    }

    return data;
}

export const deleteURLCategory = async (userToken: string, categoryId: string, url: string): Promise<GenericOutput> => {
    const response = await fetch(`/api/branch/@me/category/${categoryId}/url/${url}`, {
        method: 'DELETE',
        headers: { 'jwt-token': userToken },
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to remove url ${url} from category ${categoryId}`);
    }

    return data;
}

export const addTokenCategory = async (userToken: string, id: string, categoryId: string): Promise<GenericOutput> => {
    const response = await fetch(`/api/branch/@me/token/${id}/category`, {
        method: 'POST',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            category_id: categoryId
        }),
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to add category ${categoryId} to token with id: ${id}`);
    }

    return data;
}

export const deleteTokenCategory = async (userToken: string, id: string, categoryId: string): Promise<GenericOutput> => {
    const response = await fetch(`/api/branch/@me/token/${id}/category/${categoryId}`, {
        method: 'DELETE',
        headers: { 'jwt-token': userToken },
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to remove category ${categoryId} from token with id: ${id}`);
    }

    return data;
}

export const addCategoryParent = async (userToken: string, categoryId: string, childCategoryId: string): Promise<GenericOutput> => {
    const response = await fetch(`/api/branch/@me/category/${categoryId}/parent`, {
        method: 'POST',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            child_category_id: childCategoryId
        }),
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to add child category ${childCategoryId} to category ${categoryId}`);
    }

    return data;
}

export const deleteCategoryParent = async (userToken: string, categoryId: string, childCategoryId: string): Promise<GenericOutput> => {
    const response = await fetch(`/api/branch/@me/category/${categoryId}/parent/${childCategoryId}`, {
        method: 'DELETE',
        headers: { 'jwt-token': userToken },
    });

    const data: GenericOutput = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to remove child category ${childCategoryId} from category ${categoryId}`);
    }

    return data;
}
