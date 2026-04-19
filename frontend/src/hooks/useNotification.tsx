import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { Snackbar, Alert, AlertColor } from '@mui/material';

interface NotificationContextType {
    showError: (message: string, ttl?: number) => void;
    showSuccess: (message: string, ttl?: number) => void;
    showInfo: (message: string, ttl?: number) => void;
    showWarning: (message: string, ttl?: number) => void;
    showNotification: (message: string, severity?: AlertColor, ttl?: number) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

/**
 * Default time-to-live for notifications in milliseconds.
 */
const DEFAULT_NOTIFICATION_TTL = 10000;

export const NotificationProvider = ({ children }: { children: ReactNode }) => {
    const [open, setOpen] = useState(false);
    const [message, setMessage] = useState('');
    const [severity, setSeverity] = useState<AlertColor>('error');
    const [duration, setDuration] = useState<number>(DEFAULT_NOTIFICATION_TTL);

    const showNotification = useCallback((msg: string, sev: AlertColor = 'error', ttl: number = DEFAULT_NOTIFICATION_TTL) => {
        setMessage(msg);
        setSeverity(sev);
        setDuration(ttl);
        setOpen(true);
    }, []);

    const showError = useCallback((msg: string, ttl?: number) => showNotification(msg, 'error', ttl), [showNotification]);
    const showSuccess = useCallback((msg: string, ttl?: number) => showNotification(msg, 'success', ttl), [showNotification]);
    const showInfo = useCallback((msg: string, ttl?: number) => showNotification(msg, 'info', ttl), [showNotification]);
    const showWarning = useCallback((msg: string, ttl?: number) => showNotification(msg, 'warning', ttl), [showNotification]);

    const handleClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
        if (reason === 'clickaway') {
            return;
        }
        setOpen(false);
    };

    return (
        <NotificationContext.Provider value={{ showError, showSuccess, showInfo, showWarning, showNotification }}>
            {children}
            <Snackbar
                open={open}
                autoHideDuration={duration}
                onClose={handleClose}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert onClose={handleClose} severity={severity} variant="filled" sx={{ width: '100%' }}>
                    {message}
                </Alert>
            </Snackbar>
        </NotificationContext.Provider>
    );
};

export const useNotification = () => {
    const context = useContext(NotificationContext);
    if (context === undefined) {
        throw new Error('useNotification must be used within a NotificationProvider');
    }
    return context;
};
