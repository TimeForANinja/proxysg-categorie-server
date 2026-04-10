export const getBranches = async (): Promise<string[]> => {
    const response = await fetch('/api/branch');

    if (!response.ok) {
        throw new Error(`Failed to get branch list`);
    }

    const data = await response.json();

    if (data.status === "failed") {
        throw new Error(data.message);
    }

    return data.data;
}
