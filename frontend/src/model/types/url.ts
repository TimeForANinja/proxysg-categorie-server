export interface IMutableURL {
    hostname: string;
    description: string;
}

export interface IURL extends IMutableURL {
    id: string;
    categories: string[];
    bc_cats: string[];
}
