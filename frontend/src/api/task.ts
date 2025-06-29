/**
 * API functions for interacting with tasks
 */

const TASK_BASE_URL = '/api/task';

/**
 * Interface for task data returned from the API
 */
export interface TaskData {
  id: string;
  name: string;
  user: string;
  parameters: string[];
  status: string;
  created_at: number;
  updated_at: number;
}

/**
 * Get the status of a task
 * @param userToken - The JWT token for authentication
 * @param taskId - The ID of the task to check
 * @returns The task data
 */
export const getTaskByID = async (
  userToken: string,
  taskId: string,
): Promise<TaskData> => {
  const response = await fetch(`${TASK_BASE_URL}/${taskId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'jwt-token': userToken,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to get task status: ${response.statusText}`);
  }

  const data = await response.json();

  if (data.status === "failed") {
    throw new Error(data.message);
  }

  return data.data;
};

export const startCommit = async (
    userToken: string,
    commitMessage: string,
): Promise<string> => {
  const response = await fetch(`/api/commit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'jwt-token': userToken,
    },
    body: JSON.stringify({ message: commitMessage }),
  });

  if (!response.ok) {
    throw new Error(`Failed to get task status: ${response.statusText}`);
  }

  const data = await response.json();
  if (data.status === "failed") {
    throw new Error(data.message);
  }

  // Return the task ID
  return data.data;
}
