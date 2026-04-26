const TIME_SECONDS = 1000;

/**
 * Formats a Unix timestamp (in seconds) to a human-readable date string.
 * If the timestamp is 0, it returns 'never'.
 * @param timestamp - Unix timestamp in seconds
 */
export const formatUnixTimestamp = (timestamp: number): string => {
    if (timestamp <= 0) {
        return 'never';
    }
    const date = new Date(timestamp * TIME_SECONDS);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

export const formatUnixDateOnly = (timestamp: number): string => {
    if (timestamp <= 0) {
        return 'never';
    }
    const date = new Date(timestamp * TIME_SECONDS);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
};

// Utility method to calculate a Date-Time-Stamp to include in filenames
export const formatDateForFilename = (date: Date = new Date()): string => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed, so add 1
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return `${year}-${month}-${day}_${hours}-${minutes}-${seconds}`;
}

export const formatDateString = (date: Date | null = null): string => {
    const now = date ?? new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

export const formatDuration = (seconds: number) => {
    const secs = Math.round(seconds);
    const hours = Math.floor(secs / 3600);
    const minutes = Math.floor((secs % 3600) / 60);
    const remainingSeconds = secs % 60;
    let str = "";
    if (hours > 0) str += `${hours}h `;
    if (minutes > 0) str += `${minutes.toString().padStart(2, "0")}m `;
    if (remainingSeconds > 0 || (hours === 0 && minutes === 0)) str += `${remainingSeconds.toString().padStart(2, "0")}s`;
    return str;
}

export interface IConstraint {
    comment: string;
    start: number;
    end: number;
}

export const formatConstraintTime = (constraint?: IConstraint, fallback: string = ''): string => {
    if (!constraint) {
        return fallback;
    }
    if ((constraint.start ?? -1) < 0 && (constraint.end ?? -1) < 0) {
        return fallback;
    }
    const startDate = (constraint.start ?? -1) ? new Date(constraint.start * 1000).toISOString().split('T')[0] : '...';
    const endDate = (constraint.end ?? -1) ? new Date(constraint.end * 1000).toISOString().split('T')[0] : '...';
    return `${startDate} - ${endDate}`;
}

export const formatConstraint = (constraint?: IConstraint): string => {
    if (!constraint) {
        return '';
    }
    if (!constraint.start && !constraint.end) {
        return constraint.comment;
    }
    const comment = constraint.comment ? ` (${constraint.comment})` : '';
    return `${formatConstraintTime(constraint)}${comment}`;
};
