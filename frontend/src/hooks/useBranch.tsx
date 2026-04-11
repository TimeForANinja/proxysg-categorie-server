import React, { createContext, useContext, useState, ReactNode } from 'react';

interface BranchContextType {
    currentBranch: string;
    setCurrentBranch: (branch: string) => void;
    isLocked: boolean;
    setLocked: (locked: boolean) => void;
}

const UseBranch = createContext<BranchContextType | undefined>(undefined);

export const BranchProvider = ({ children }: { children: ReactNode }) => {
    // Default branch is "b_prod"
    const [currentBranch, setCurrentBranch] = useState<string>('b_prod');
    const [isLocked, setLocked] = useState<boolean>(false);

    return (
        <UseBranch.Provider value={{ currentBranch, setCurrentBranch, isLocked, setLocked }}>
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
