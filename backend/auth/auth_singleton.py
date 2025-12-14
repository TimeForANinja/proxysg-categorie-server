from apiflask import APIFlask
from typing import List, Callable, Any
import importlib
import pkgutil

from auth.auth import AuthHandler
from auth.auth_realm import AuthRealmInterface
from auth.util.jwt_singleton import get_jwt_handler
from log import log_error


def _discover_auth_modules() -> List[Any]:
    """
    Discover all modules under the `auth` package whose name ends with `_auth`.
    Returns the imported module objects.
    """
    modules: List[Any] = []
    import auth as auth_pkg  # root package for auth providers
    for finder, name, ispkg in pkgutil.walk_packages(auth_pkg.__path__, auth_pkg.__name__ + "."):
        # Only consider leaf modules that end with `_auth`
        if not ispkg and name.endswith("_auth"):
            try:
                mod = importlib.import_module(name)
                # Only keep modules exposing the required plugin API
                if hasattr(mod, 'auth_fits') and hasattr(mod, 'build_auth_realm'):
                    modules.append(mod)
            except Exception as e:
                # If a module fails to import, log an error and skip
                log_error("AUTH", "Failed to import auth provider: " + name, e)
    return modules


def _select_provider(modules: List[Any], app: APIFlask, auth_type: str) -> Any:
    """
    Pick the first module whose `auth_fits(app, auth_type)` returns True.
    """
    for mod in modules:
        try:
            if callable(getattr(mod, 'auth_fits', None)) and mod.auth_fits(app, auth_type):
                return mod
        except Exception as e:
            # ignore faulty providers
            log_error("AUTH", "Failed to check auth provider: " + mod.__name__, e)
    return None


def get_auth_if(app: APIFlask) -> AuthHandler:
    """
    Get the Auth Interface as a singleton
    """
    with app.app_context():
        auth_if = app.config.get('SINGLETONS', {}).get('AUTH', None)

        if auth_if is None:
            # auth_if not yet defined, so build a new one

            jwt = get_jwt_handler(app)
            realms: List[AuthRealmInterface] = []

            # read all auth providers from sub directories
            providers = _discover_auth_modules()

            # auth order is a list of all auth realms configured
            # the order determines the priority
            auth_order = app.config.get('AUTH', {}).get('ORDER', 'local')

            for auth_type in auth_order.split(','):
                auth_type = auth_type.strip().lower()
                provider = _select_provider(providers, app, auth_type)
                if provider is None:
                    log_error("AUTH", "Unsupported APP_AUTH_ORDER TYPE: " + auth_type)
                    # ignore unknown types
                    continue

                # Build the realm using the provider's factory
                build_fn: Callable[[APIFlask, Any], AuthRealmInterface] = getattr(provider, 'build_auth_realm')
                realm = build_fn(app, jwt)
                if realm is None:
                    log_error("AUTH", "Provider failed to build realm for type: " + auth_type)
                    # ignore providers that fail to build realms
                    continue
                realms.append(realm)

            # cast the realms to the auth handler and safe in the global context for the singleton
            auth_if = AuthHandler(realms)
            app.config.setdefault('SINGLETONS', {})
            app.config['SINGLETONS']['AUTH'] = auth_if

        return auth_if
