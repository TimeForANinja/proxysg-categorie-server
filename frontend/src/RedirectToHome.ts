import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export function RedirectToHome() {
    const navigate = useNavigate();

    useEffect(() => {
        // Redirect to "/" on rendering this component
        navigate("/");
    }, [navigate]);

    return null; // Component renders nothing
}
