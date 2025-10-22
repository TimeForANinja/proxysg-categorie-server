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
