export interface ITask {
    id: string;
    name: string;
    user: string;
    parameters: string[];
    status: string;
    created_at: number;
    updated_at: number;
}
