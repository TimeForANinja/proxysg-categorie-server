import React from 'react';
import { getTaskByID } from '../../api/task';
import { ITask } from '../../model/types/task';

// Polling defaults
const TIME_SECONDS = 1000;
const DEFAULT_POLL_INTERVAL = 1 * TIME_SECONDS;

export type TaskLifecycleStatus = 'pending' | 'running' | 'success' | 'failed';

export interface TaskStatusTrackerOptions {
  // Polling interval in ms
  intervalMs?: number;
}

export interface UseTaskStatusTrackerProps {
  token?: string | null;
  taskId?: string;
  options?: TaskStatusTrackerOptions;
  // Callbacks for status changes. Each receives the full task object
  onPending?: (task: ITask) => void;
  onRunning?: (task: ITask) => void;
  onSuccess?: (task: ITask) => void;
  onFailed?: (task: ITask) => void;
  // Called once when the task reaches a terminal state (success/failed)
  onComplete?: (task: ITask) => void;
  // Called when an error occurs fetching status
  onError?: (error: unknown) => void;
}

export interface UseTaskStatusTrackerResult {
  lastTask?: ITask;
  lastError?: unknown;
  status?: TaskLifecycleStatus;
  isActive: boolean;
}

/**
 * A reusable hook that polls a task's status by taskId and emits lifecycle callbacks.
 */
export function useTaskStatusTracker(props: UseTaskStatusTrackerProps): UseTaskStatusTrackerResult {
  const { token, taskId, options, onPending, onRunning, onSuccess, onFailed, onComplete, onError } = props;

  const intervalMs = options?.intervalMs ?? DEFAULT_POLL_INTERVAL;

  const [lastTask, setLastTask] = React.useState<ITask | undefined>(undefined);
  const [status, setStatus] = React.useState<TaskLifecycleStatus | undefined>(undefined);
  const [lastError, setLastError] = React.useState<unknown>(undefined);

  const isTerminal = (s?: TaskLifecycleStatus) => s === 'success' || s === 'failed';

  React.useEffect(() => {
    // Do nothing if no token or no task to track
    if (!token || !taskId) return;

    let cancelled = false;
    const timer = setInterval(async () => {
      if (!token || !taskId) return; // guard while running
      try {
        const taskData = await getTaskByID(token, taskId);
        if (cancelled) return;

        setLastTask(taskData);
        const nextStatus = (taskData.status as TaskLifecycleStatus) ?? 'pending';
        setStatus(nextStatus);

        switch (nextStatus) {
          case 'success':
            onSuccess?.(taskData);
            onComplete?.(taskData);
            break;
          case 'failed':
            onFailed?.(taskData);
            onComplete?.(taskData);
            break;
          case 'running':
            onRunning?.(taskData);
            break;
          default:
          case 'pending':
            onPending?.(taskData);
            break;
        }

        // Stop polling when reaching a terminal state
        if (isTerminal(nextStatus)) {
          clearInterval(timer);
        }
      } catch (err) {
        if (cancelled) return;
        setLastError(err);
        onError?.(err);
      }
    }, intervalMs);

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [token, taskId, intervalMs, onPending, onRunning, onSuccess, onFailed, onComplete, onError]);

  return {
    lastTask,
    lastError,
    status,
    isActive: Boolean(token && taskId && !isTerminal(status)),
  };
}

export interface TaskStatusTrackerProps extends UseTaskStatusTrackerProps {
  // Optional render function to display the current status/UI
  children?: (result: UseTaskStatusTrackerResult) => React.ReactNode;
}

/**
 * Component wrapper for the useTaskStatusTracker hook.
 * Can be dropped anywhere to start tracking a task by id.
 */
export const TaskStatusTracker: React.FC<TaskStatusTrackerProps> = ({ children, ...hookProps }) => {
  const result = useTaskStatusTracker(hookProps);
  return <>{children ? children(result) : null}</>;
};
