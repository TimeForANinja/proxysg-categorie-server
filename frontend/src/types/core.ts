import { ICategory } from "./category";

export interface RestTestResult {
    input: string;
    normalized_input: string;
    matched_url: string;
    local_categories: ICategory[];
    bc_categories: string[];
}
