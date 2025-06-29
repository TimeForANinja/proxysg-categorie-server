import React from 'react';
import { Alert } from '@mui/material';
import { getTaskByID } from '../../api/task';
import { useAuth } from '../../model/AuthContext';

const TIME_SECONDS = 1000;
const TIME_CHECK_TASKS = 2 * TIME_SECONDS;


interface TaskStatusProps {
  taskId: string;
  onTaskComplete: (success: boolean) => void;
  successMessage?: string;
  failureMessage?: string;
}
const TaskStatus: React.FC<TaskStatusProps> = ({ 
  taskId,
  onTaskComplete, 
  successMessage = 'Task completed successfully!',
  failureMessage = 'Task failed. Please try again.'
}) => {
  const { token } = useAuth();
  const [error, setError] = React.useState<string | null>(null);
  const [warning, setWarning] = React.useState<string | null>(null);
  const [success, setSuccess] = React.useState<string | null>(null);

  // ref to the current task id
  // resolves various problems with pass-by-value we can run into
  // with setInterval and a function defined inside the react fragment
  const taskIdRef = React.useRef(taskId);

  const checkTaskStatus = React.useCallback(async () => {
    // only (continue to) check status if we have a pending task
    if (!taskIdRef.current || !token) return;
    try {
      // fetch the task and set the success / warning / error banner accordingly
      const taskData = await getTaskByID(token, taskIdRef.current);
      switch (taskData.status) {
        case 'success':
          setSuccess(successMessage);
          setWarning(null);
          setError(null);
          // Call the onTaskComplete callback
          onTaskComplete(true);
          break;
        case 'failed':
          setSuccess(null);
          setWarning(null);
          setError(failureMessage);
          // Call the onTaskComplete callback
          onTaskComplete(false);
          break;
        case 'running':
          setSuccess(null);
          setWarning('Waiting for execution to finish...');
          setError(null);
          break;
        default:
        case 'pending':
          setSuccess(null);
          setWarning('Waiting for execution to start...');
          setError(null);
          break;
      }
    } catch (err) {
      setSuccess(null);
      setWarning(null);
      setError(`Failed to get task status: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  }, [failureMessage, onTaskComplete, successMessage, token]);

  React.useEffect(() => {
    // update the ref
    taskIdRef.current = taskId;
    // Immediately check status when taskId changes
    checkTaskStatus();
  }, [taskId, checkTaskStatus])

  // Interval to check for the state of the task
  React.useEffect(() => {
    const timer = setInterval(() => {
      checkTaskStatus();
    }, TIME_CHECK_TASKS);
    // return a function that gets called to "cleanup" the effect
    return () => clearInterval(timer);
  }, [checkTaskStatus]);

  return (
    <>
      {error && <Alert severity="error">{error}</Alert>}
      {warning && <Alert severity="warning">{warning}</Alert>}
      {success && <Alert severity="success">{success}</Alert>}
    </>
  );
};

export default TaskStatus;
