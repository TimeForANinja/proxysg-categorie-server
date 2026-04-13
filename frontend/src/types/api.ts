export type Status = 'success' | 'failed';

export interface GenericOutput {
    message: string;
    status: Status;
}

export interface DataOutput<T> extends GenericOutput {
    data: T;
}
