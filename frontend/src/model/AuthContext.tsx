import React, {createContext, useContext} from "react";
import {OptBoolean} from "./OptionalBool";
import {IUser, readLoginToken, removeLoginToken, saveLoginToken} from "./loginHandler";
import {checkLogin, doLogin} from "../api/auth";

class GenericContextClass<T> {
    protected readonly _state: T;
    protected readonly _setState: (state: T) => void;

    constructor(state: T, setState: (state: T) => void) {
        this._state = state;
        this._setState = setState
    }
}

interface AuthState {
    loggedIn: OptBoolean;
    user: IUser | null;
}

class AuthManager extends GenericContextClass<AuthState> {
    // Method to get login status
    get loggedIn(): OptBoolean {
        return this._state.loggedIn;
    }

    // Method to get current username
    get username(): string | undefined {
        return this._state.user?.username;
    }

    get token(): string | undefined {
        return this._state.user?.token;
    }

    // Method to log in a user (updates login state and username)
    async login(username: string, password: string): Promise<IUser> {
        const user = await doLogin(username, password)

        saveLoginToken(user)
        this._setState({
            loggedIn: OptBoolean.Yes,
            user: user,
        })

        return user;
    }

    // Method to log out a user
    logout(): void {
        removeLoginToken();
        this._setState({
            loggedIn: OptBoolean.No,
            user: null,
        })
    }

    // Load Session from Browser Storage
    static async getInitialState(): Promise<AuthState> {
        // Fetch the user username and token from local storage
        const user = readLoginToken();

        // If the token/username does not exist, mark the user as logged out
        if (!user || !user.token) {
            return {
                loggedIn: OptBoolean.No,
                user: null,
            }
        }

        const valid = await checkLogin(user.token);

        return {
            user: valid ? user : null,
            loggedIn: valid ? OptBoolean.Yes : OptBoolean.No,
        }
    }
}

// Create the context; default it to `null`
const AuthContext = createContext<AuthManager | null>(null);

// Create a provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [isState, setState] = React.useState<AuthState>({
        loggedIn: OptBoolean.Unknown,
        user: null,
    });

    const authManager = React.useMemo(() => {
        return new AuthManager(isState, setState);
    }, [isState, setState]);

    React.useEffect(() => {
        AuthManager.getInitialState().then(state => setState(state));
    },[])

    return (
        <AuthContext.Provider value={authManager}>
            {children}
        </AuthContext.Provider>
    );
};

// Helper hook to use the context
export const useAuth = (): AuthManager => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthManager");
    }
    return context;
};
