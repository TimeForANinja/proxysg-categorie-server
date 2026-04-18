from apiflask import APIFlask
from typing import List, Union
import importlib
import pkgutil

from auth.auth import AuthHandler
from auth.auth_realm import AuthRealmInterface, AuthProviderInterface
from auth.jwt.jwt_singleton import get_jwt_handler
from util.log import log_error, log_debug


def _discover_auth_modules() -> List[AuthProviderInterface]:
    """
    Discover all auth modules within the `auth` package.
    Modules must be located in a subfolder, and their filename must end with `_auth.py`.
    Each module must define an `AuthProvider` class that implements `AuthProviderInterface`.
    """
    providers: List[AuthProviderInterface] = []
    import auth as auth_pkg  # root package for auth providers
    for finder, name, is_pkg in pkgutil.walk_packages(auth_pkg.__path__, auth_pkg.__name__ + "."):
        # Only consider leaf modules that end with `_auth`
        if not is_pkg and name.endswith("_auth"):
            try:
                mod = importlib.import_module(name)
                # Ensure the module provides an AuthProvider class
                if hasattr(mod, 'AuthProvider'):
                    provider_cls = getattr(mod, 'AuthProvider')
                    # Instantiate the provider
                    provider = provider_cls()
                    # Make sure the provider implements AuthProviderInterface
                    if isinstance(provider, AuthProviderInterface):
                        providers.append(provider)
                    else:
                        log_error("AUTH", f"Provider class in '{name}' does not implement AuthProviderInterface")
            except Exception as e:
                log_error("AUTH", f"Failed to import auth provider: {name}", e)
    return providers


def _select_provider(providers: List[AuthProviderInterface], app: APIFlask, auth_type: str) -> Union[AuthProviderInterface, None]:
    """
    Select the provider that matches the requested `auth_type`.
    """
    for provider in providers:
        try:
            if provider.auth_fits(app, auth_type):
                return provider
        except Exception as e:
            log_error("AUTH", f"Error checking provider '{type(provider).__name__}': {e}")
    return None


def get_auth_if(app: APIFlask) -> AuthHandler:
    """
    Singleton factory for the AuthHandler.
    Initializes realms based on the application configuration (`AUTH: ORDER`).
    """
    with app.app_context():
        auth_if = app.config.get('SINGLETONS', {}).get('AUTH', None)

        if auth_if is None:
            jwt = get_jwt_handler(app)
            realms: List[AuthRealmInterface] = []

            # Discover all available auth modules
            providers = _discover_auth_modules()
            log_debug("AUTH", f"Discovered {len(providers)} auth providers")

            # Configuration defines the priority and selection of realms
            auth_order = app.config.get('AUTH', {}).get('ORDER', 'local')

            for auth_type in auth_order.split(','):
                auth_type = auth_type.strip().lower()
                provider = _select_provider(providers, app, auth_type)

                if provider is None:
                    log_error("AUTH", f"No provider found for auth type: {auth_type}")
                    continue

                # Instantiate the realm using the provider's factory
                try:
                    realm = provider.build_auth_realm(app, jwt)
                    if realm:
                        realms.append(realm)
                    else:
                        log_error("AUTH", f"Provider '{type(provider).__name__}' returned empty realm for type: {auth_type}")
                except Exception as e:
                    log_error("AUTH", f"Failed to build realm for type '{auth_type}': {e}")

            # Initialize the handler with the successfully built realms
            auth_if = AuthHandler(realms)
            app.config.setdefault('SINGLETONS', {})
            app.config['SINGLETONS']['AUTH'] = auth_if

        return auth_if
