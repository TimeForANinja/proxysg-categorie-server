import React, { createContext, useContext, useState, ReactNode } from 'react';

interface BranchContextType {
    currentBranch: string;
    setCurrentBranch: (branch: string) => void;
    isLocked: boolean;
    setLocked: (locked: boolean) => void;
}

const BranchContext = createContext<BranchContextType | undefined>(undefined);

export const BranchProvider = ({ children }: { children: ReactNode }) => {
    // Default branch can be "main" or empty, depending on server default
    const [currentBranch, setCurrentBranch] = useState<string>('main');
    const [isLocked, setLocked] = useState<boolean>(false);

    return (
        <BranchContext.Provider value={{ currentBranch, setCurrentBranch, isLocked, setLocked }}>
            {children}
        </BranchContext.Provider>
    );
};

export const useBranch = () => {
    const context = useContext(BranchContext);
    if (context === undefined) {
        throw new Error('useBranch must be used within a BranchProvider');
    }
    return context;
};
