import {TASK_BASE_URL} from "./task";

const NEW_TASK_BASE_URL = `${TASK_BASE_URL}/new`

export const loadExisting = async (
    userToken: string,
    text: string,
    prefix: string,
): Promise<string> => {
    // Create the request body as JSON
    const requestBody: { categoryDB: string; prefix: string } = {
        categoryDB: text,
        prefix,
    };

    const response = await fetch(`${NEW_TASK_BASE_URL}/upload_existing_db`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
        },
        body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
        throw new Error(`Failed to import existing URLs`);
    }

    const data = await response.json();
    if (data.status === "failed") {
        throw new Error(data.message);
    }

    // Return the task ID
    return data.data;
}

export enum CleanupFlags {
    Categories = 1 << 0,
    URLs = 1 << 1,
}

export const cleanupUnused = async (
    userToken: string,
    flags: CleanupFlags,
): Promise<string> => {
    // Create the request body as JSON
    const requestBody: { flags: CleanupFlags } = {
        flags,
    };

    const response = await fetch(`${NEW_TASK_BASE_URL}/cleanup_unused`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
        },
        body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
        throw new Error(`Failed to import existing URLs`);
    }

    const data = await response.json();
    if (data.status === "failed") {
        throw new Error(data.message);
    }

    // Return the task ID
    return data.data;
}
