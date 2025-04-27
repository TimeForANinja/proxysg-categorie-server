const LOAD_EXISTING_BASE_URL = '/api/upload_existing_db'

export const loadExisting = async (
    userToken: string,
    text: string,
    prefix: string,
): Promise<void> => {
    // Create the request body as JSON
    const requestBody: { categoryDB: string; prefix: string } = {
        categoryDB: text,
        prefix,
    };

    const response = await fetch(LOAD_EXISTING_BASE_URL, {
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
}
