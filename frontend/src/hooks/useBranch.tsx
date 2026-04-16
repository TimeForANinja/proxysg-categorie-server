import React, { createContext, useContext, useState, ReactNode } from 'react';

interface BranchContextType {
    currentBranch: string;
    setCurrentBranch: (branch: string) => void;
    isLocked: boolean;
    setIsLocked: (locked: boolean) => void;
}

const UseBranch = createContext<BranchContextType | undefined>(undefined);

export const BranchProvider = ({ children }: { children: ReactNode }) => {
    const [currentBranch, setCurrentBranch] = useState<string>(readBranch());
    const [isLocked, setIsLocked] = useState<boolean>(false);

    const set_branch_wrapper = React.useCallback((branch: string) => {
        saveBranch(branch);
        setCurrentBranch(branch);
    }, [setCurrentBranch]);

    return (
        <UseBranch.Provider value={{ currentBranch, setCurrentBranch: set_branch_wrapper, isLocked, setIsLocked }}>
            {children}
        </UseBranch.Provider>
    );
};

export const useBranch = () => {
    const context = useContext(UseBranch);
    if (context === undefined) {
        throw new Error('useBranch must be used within a BranchProvider');
    }
    return context;
};

const LOCAL_STORAGE_KEY_BRANCH = 'app_branch';
export const DEFAULT_BRANCH = 'b_prod';

export const readBranch = (): string => {
    return JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY_BRANCH) ?? '{}')?.branch ?? DEFAULT_BRANCH;
}

export const removeBranch = () => {
    localStorage.removeItem(LOCAL_STORAGE_KEY_BRANCH)
}

export const saveBranch = (branch: string) => {
    localStorage.setItem(LOCAL_STORAGE_KEY_BRANCH, JSON.stringify({ branch }));
}
