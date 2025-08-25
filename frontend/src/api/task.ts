/**
 * API functions for interacting with tasks
 */
import {ITask} from "../model/types/task";

export const TASK_BASE_URL = '/api/task';


/**
 * Get the status of a task
 * @param userToken - The JWT token for authentication
 * @param taskId - The ID of the task to check
 * @returns The task data
 */
export const getTaskByID = async (
  userToken: string,
  taskId: string,
): Promise<ITask> => {
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

/**
 * Get the list of all tasks
 * @param userToken - The JWT token for authentication
 * @returns The list of tasks
 */
export const getTasks = async (
    userToken: string
): Promise<ITask[]> => {
    const response = await fetch(TASK_BASE_URL, {
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
}
