
export interface ICategory {
    id: number;
    name: string;
    color: number;
    description: string;
}

/*

interface ICategory {
    value: number;
    label: string;
}

*/

export const getCategories = async (): Promise<ICategory[]> => {
    const response = await fetch('http://127.0.0.1:3080/api/categories');
    const data = await response.json();
    return data.data;
}
