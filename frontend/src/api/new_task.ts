const TASK_BASE_URL = '/api/new-task/'

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

    const response = await fetch(`${TASK_BASE_URL}/upload_existing_db`, {
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

export const doCleanupUnused = async (
    userToken: string,
): Promise<string> => {
    const response = await fetch(`${TASK_BASE_URL}/cleanup_unused`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'jwt-token': userToken,
        },
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
