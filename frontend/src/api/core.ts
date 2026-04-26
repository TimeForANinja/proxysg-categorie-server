import {DataOutput, GenericOutput} from "../types/api";
import {RestTestResult} from "../types/core";

export type IMetricsData = { [key: string]: any };

export const getMetrics = async (userToken: string): Promise<IMetricsData> => {
    const response = await fetch('/api/metrics', {
        headers: { 'jwt-token': userToken },
    });

    if (!response.ok) {
        const data: DataOutput<IMetricsData> = await response.json().catch(() => ({}));
        throw new Error(data.message || `Failed to get metrics`);
    }

    const data: DataOutput<IMetricsData> = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message || `Failed to get metrics`);
    }

    return data.data;
}

export const cleanupCore = async (userToken: string): Promise<GenericOutput> => {
    const response = await fetch('/api/cleanup-core', {
        method: 'POST',
        headers: { 'jwt-token': userToken },
    });

    if (!response.ok) {
        const data: GenericOutput = await response.json().catch(() => ({}));
        throw new Error(data.message || `Failed to cleanup core`);
    }

    const data: GenericOutput = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message || `Failed to cleanup core`);
    }

    return data;
}

export const compileToken = async (userToken: string, tokenUuid: string): Promise<GenericOutput> => {
    const response = await fetch(`/api/compile/${tokenUuid}`, {
        method: 'POST',
        headers: { 'jwt-token': userToken },
    });

    if (!response.ok) {
        const data: GenericOutput = await response.json().catch(() => ({}));
        throw new Error(data.message || `Failed to compile token ${tokenUuid}`);
    }

    const data: GenericOutput = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message || `Failed to compile token ${tokenUuid}`);
    }

    return data;
}

export const testApi = async (userToken: string, urls: string[]): Promise<RestTestResult[]> => {
    const response = await fetch('/api/test', {
        method: 'POST',
        headers: {
            'jwt-token': userToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ urls }),
    });

    if (!response.ok) {
        const data: DataOutput<RestTestResult[]> = await response.json().catch(() => ({}));
        throw new Error(data.message || `Failed to test api`);
    }

    const data: DataOutput<RestTestResult[]> = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message || `Failed to test api`);
    }

    return data.data;
}
