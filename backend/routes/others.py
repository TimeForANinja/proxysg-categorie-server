from apiflask import APIBlueprint

from auth.auth_singleton import get_auth_if
from db.db_singleton import get_db
from db.dbmodel.url import FAILED_LOOKUP
from log import log_debug
from background.query_bc import do_query
from background.background_tasks import get_bc_credentials
from routes.schemas.other import TestURIOutput


def add_others_bp(app):
    log_debug('ROUTES', 'Adding Others Blueprint')
    auth_if = get_auth_if(app)
    others_bp = APIBlueprint('others', __name__)

    # Route to test a URL for it's Categories
    @others_bp.get('/api/test-uri/<string:value>')
    @others_bp.doc(summary='Test URL', description='Test a URL against the local DB and Bluecoat DB')
    @others_bp.output(TestURIOutput)
    @others_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RO])
    def handle_test_uri(value: str):
        db_if = get_db()

        # 1) Normalize input to a hostname
        hostname = value.strip().lower()

        # 2) Fetch all URLs and select the best match by comparing the longest suffix that matched
        urls = db_if.urls.get_all_urls()
        best_url = None
        best_len = -1
        for u in urls:
            if hostname == u.hostname:
                # perfect match, so stop the search
                best_url = u
                break
            if hostname.endswith('.' + u.hostname):
                # we've found part of the hostname
                score = len(u.hostname)
                # only save if this is the best we've found
                if score > best_len:
                    best_len = score
                    best_url = u

        # 3) Fetch all categories and map matched URL categories
        matching_categories = []
        if best_url is not None:
            all_categories = db_if.categories.get_all_categories()
            categories_by_id = {c.id: c for c in all_categories}

            # initial list of IDs
            seed_ids = list(best_url.categories or [])
            # tracker for IDs visited, and IDs we still need to visit
            visited: set[str] = set()
            stack = list(seed_ids)

            while stack:
                # get the next ID to investigate
                cid = stack.pop()

                # check against the "visited" tracker
                if cid in visited:
                    continue
                visited.add(cid)

                c = categories_by_id.get(cid)
                if c is None:
                    continue

                matching_categories.append(c)

                # enqueue nested sub-categories (descendants)
                for nested_id in c.nested_categories:
                    if nested_id not in visited:
                        stack.append(nested_id)

        # 4) Query BlueCoat category for the provided hostname
        credentials = get_bc_credentials(app)
        bc_categories = [FAILED_LOOKUP]
        try:
            bc_categories = do_query(credentials, hostname)
        except Exception:
            # keep FAILED_LOOKUP on any unexpected error
            pass

        # 5) Build response
        return {
            'status': 'success',
            'message': 'successfully matched URL against Database',
            'data': {
                'input': value,
                'matched_url': best_url,
                'local_categories': matching_categories,
                'bc_categories': bc_categories,
            }
        }

    app.register_blueprint(others_bp)
