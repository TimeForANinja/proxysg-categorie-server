import React from 'react';
import './login.css';
import {useNavigate} from 'react-router-dom'
import {OptBoolean} from "../../types/OptionalBool";
import {useAuth} from "../../hooks/useLogin";
import {getAuthMechanisms} from "../../api/auth";
import {IAuthMechanism, IAuthUIComponent} from "../../types/auth";


function LoginPage() {
    const authMgmt = useAuth();
    const navigate = useNavigate();

    const [mechanisms, setMechanisms] = React.useState<IAuthMechanism[]>([]);
    const [formData, setFormData] = React.useState<Record<string, string>>({});
    const [errors, setErrors] = React.useState<Record<string, string>>({});
    const [loading, setLoading] = React.useState<boolean>(true);

    React.useEffect(() => {
        if (authMgmt.loggedIn === OptBoolean.Yes) {
            navigate('/');
        }
    }, [authMgmt.loggedIn, navigate])

    React.useEffect(() => {
        getAuthMechanisms().then(setMechanisms).catch(console.error).finally(() => setLoading(false));
    }, []);

    const onSendLogin = (mechanism: IAuthMechanism) => {
        setErrors({});

        // Simple validation: check if all required keys are present
        const mechanismErrors: Record<string, string> = {};
        mechanism.ui.forEach(comp => {
            if ((comp.type === 'input-text' || comp.type === 'input-password') && comp.key) {
                if (!formData[comp.key]) {
                    mechanismErrors[comp.key] = `${comp.label || comp.key} is required`;
                }
            }
        });

        if (Object.keys(mechanismErrors).length > 0) {
            setErrors(mechanismErrors);
            return;
        }

        authMgmt.login({...formData, type: mechanism.type}).then(() => {
            navigate('/')
        }).catch((err) => {
            setErrors({general: err.message});
        });
    }

    const handleKeyDown = (event: React.KeyboardEvent, mechanism: IAuthMechanism) => {
        if (event.key === 'Enter') {
            onSendLogin(mechanism);
        }
    }

    const renderComponent = (comp: IAuthUIComponent, mechanism: IAuthMechanism) => {
        switch (comp.type) {
            case 'input-text':
            case 'input-password':
                return (
                    <div key={comp.key} className={'inputWrapper'}>
                        {comp.label && <label className={'inputLabel'}>{comp.label}</label>}
                        <input
                            type={comp.type === 'input-password' ? 'password' : 'text'}
                            value={comp.key ? (formData[comp.key] || '') : ''}
                            placeholder={comp.label}
                            onChange={(ev) => comp.key && setFormData({...formData, [comp.key]: ev.target.value})}
                            onKeyDown={(ev) => handleKeyDown(ev, mechanism)}
                            className={'inputBox'}
                        />
                        {comp.key && <label className="errorLabel">{errors[comp.key]}</label>}
                    </div>
                );
            case 'button':
                return (
                    <div key={comp.label} className={'buttonWrapper'}>
                        <button
                            className={'loginButton'}
                            type="button"
                            onClick={() => {
                                if (comp.location) {
                                    window.location.href = comp.location;
                                } else {
                                    onSendLogin(mechanism);
                                }
                            }}
                        >
                            {comp.label || 'Log in'}
                        </button>
                    </div>
                );
            default:
                return null;
        }
    }

    if (loading) {
        return (
            <div className={'mainContainer'}>
                <div className={'loginCard'}>
                    <div className={'loading'}>Loading...</div>
                </div>
            </div>
        );
    }

    return (
        <div className={'mainContainer'}>
            <div className={'loginCard'}>
                <div className={'titleContainer'}>
                    <div>Login</div>
                </div>
                {errors.general && <div className="errorLabel generalError">{errors.general}</div>}

                {mechanisms.map(mech => {
                    const hasInputs = mech.ui.some(c => c.type === 'input-text' || c.type === 'input-password');
                    const hasButton = mech.ui.some(c => c.type === 'button');

                    return (
                        <div key={mech.type} className={'mechanismContainer'}>
                            <h3 className={'mechanismTitle'}>{mech.label}</h3>
                            <div className={'mechanismUI'}>
                                {mech.ui.map(comp => renderComponent(comp, mech))}
                                {hasInputs && !hasButton && (
                                    <div className={'buttonWrapper'}>
                                        <button
                                            className={'loginButton'}
                                            type="button"
                                            onClick={() => onSendLogin(mech)}
                                        >
                                            Login
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

export default LoginPage;
