import React from 'react';
import { getTaskByID } from '../../api/task';
import {Alert} from "@mui/material";
import {useAuth} from "../../model/AuthContext";

// Polling defaults
const TIME_SECONDS = 1000;
const DEFAULT_POLL_INTERVAL = 1 * TIME_SECONDS;

export type TaskLifecycleStatus = 'pending' | 'running' | 'success' | 'failed';
const isTerminal = (s?: TaskLifecycleStatus) => s === 'success' || s === 'failed';

export interface taskStatusProps {
    title: string;
    taskId: string | null;
    // Called once when the task reaches a terminal state (success/failed)
    onComplete: () => void;
    // Polling interval in ms
    intervalMs?: number // = DEFAULT_POLL_INTERVAL;
}

export const TaskStatusTracker = (props: taskStatusProps) => {
    const { token } = useAuth();
    const [error, setError] = React.useState<string | null>(null);
    const [warning, setWarning] = React.useState<string | null>(null);
    const [success, setSuccess] = React.useState<string | null>(null);

    const {taskId, title, onComplete} = props;
    const intervalMs = props?.intervalMs ?? DEFAULT_POLL_INTERVAL;

    React.useEffect(() => {
        // Do nothing if no token or no task to track
        if (!token || !taskId) return;

        let cancelled = false;
        const timer = setInterval(async () => {
            if (!token || !taskId) return; // guard while running
            try {
                const taskData = await getTaskByID(token, taskId);
                if (cancelled) return;

                const nextStatus = (taskData.status as TaskLifecycleStatus) ?? 'pending';

                switch (nextStatus) {
                    case 'success':
                        setSuccess(title+' uploaded successfully!');
                        setWarning(null);
                        setError(null);
                        onComplete();
                        break;
                    case 'failed':
                        setSuccess(null);
                        setWarning(null);
                        setError(title+' failed. Please try again.');
                        onComplete();
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

                // Stop polling when reaching a terminal state
                if (isTerminal(nextStatus)) {
                    clearInterval(timer);
                }
            } catch (err) {
                if (cancelled) return;
                setSuccess(null);
                setWarning(null);
                setError(title+' failed. Please try again.');
                onComplete();
            }
        }, intervalMs);

        return () => {
            cancelled = true;
            clearInterval(timer);
        };
    }, [token, title, taskId, intervalMs, onComplete]);

    return <>
        { error && (<Alert severity="error">{error}</Alert>)}
        { warning && (<Alert severity="warning">{warning}</Alert>)}
        { success && (<Alert severity="success">{success}</Alert>)}
    </>;
};
