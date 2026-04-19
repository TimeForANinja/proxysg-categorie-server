import {DataOutput} from "../types/api";

export type IMetricsData = { [key: string]: any };

export const getMetrics = async (userToken: string): Promise<IMetricsData> => {
    const response = await fetch('/api/metrics', {
        headers: { 'jwt-token': userToken },
    });
    const data: DataOutput<IMetricsData> = await response.json();

    if (!response.ok || data.status === "failed") {
        throw new Error(data.message || `Failed to get metrics`);
    }

    return data.data;
}
