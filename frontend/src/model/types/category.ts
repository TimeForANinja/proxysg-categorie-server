export interface IMutableCategory {
    name: string;
    color: number;
    description: string;
}

export interface ICategory extends IMutableCategory {
    id: string;
    nested_categories: string[];
}
