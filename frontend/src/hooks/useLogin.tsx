import React, {createContext, useContext} from "react";
import {CircularProgress} from "@mui/material";
import {OptBoolean} from "../types/OptionalBool";
import {ILoginOutputData} from "../types/auth";
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
    loginData: ILoginOutputData | null;
}

class AuthManager extends GenericContextClass<AuthState> {
    // Method to get login status
    get loggedIn(): OptBoolean {
        return this._state.loggedIn;
    }

    // Method to get current username
    get username(): string {
        return this._state.loginData?.user?.username ?? 'Unknown';
    }

    get token(): string {
        return this._state.loginData?.token ?? '';
    }

    // Method to log in a user (updates login state and username)
    async login(loginData: Record<string, string>): Promise<ILoginOutputData> {
        const data = await doLogin(loginData)

        saveLoginToken(data)
        this._setState({
            loggedIn: OptBoolean.Yes,
            loginData: data,
        })

        return data;
    }

    // Method to log out a user
    logout(): void {
        removeLoginToken();
        this._setState({
            loggedIn: OptBoolean.No,
            loginData: null,
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
                loginData: null,
            }
        }

        const valid = await checkLogin(user.token);

        return {
            loginData: valid ? user : null,
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
        loginData: null,
    });

    const authManager = React.useMemo(() => {
        return new AuthManager(isState, setState);
    }, [isState, setState]);

    React.useEffect(() => {
        AuthManager.getInitialState().then(state => setState(state));
    }, []);

    if (authManager.loggedIn === OptBoolean.Unknown) {
        return (
            <div
                style={{
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    alignItems: 'center',
                    height: '100vh',
                }}
            >
                <CircularProgress />
                <div>Checking Authentication...</div>
            </div>
        );
    }

    return (
        <AuthContext.Provider value={authManager}>
            {children}
        </AuthContext.Provider>
    );
};

// small wrapper to use the auth context in a component
export const useAuth = (): AuthManager => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthManager");
    }
    return context;
};

const LOCAL_STORAGE_KEY_USER = 'app_user';

export const readLoginToken = (): ILoginOutputData => {
    return JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY_USER) ?? '{}');
}

export const removeLoginToken = () => {
    localStorage.removeItem(LOCAL_STORAGE_KEY_USER)
}

export const saveLoginToken = (user: ILoginOutputData) => {
    localStorage.setItem(LOCAL_STORAGE_KEY_USER, JSON.stringify(user));
}
