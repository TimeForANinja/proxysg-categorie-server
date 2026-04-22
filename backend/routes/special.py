import platform
import datetime as dt
from typing import cast
import psutil
from apiflask import APIBlueprint, APIFlask

from auth.auth_roles import AuthRoles
from auth.auth_singleton import get_auth_if
from auth.auth_user import AuthUser
from db.db_singleton import get_db
from model.util.error import ModelError
from model.util.parse_localdb import parse_db
from routes.schemas.error import ErrorResponse
from util.log import log_debug
from model.special import ERROR_NOT_FOUND, ERROR_UNCHANGED
from routes.schemas.special import list_metrics_output_schema, ListMetricsOutput, existing_db_input_schema, \
    ExistingDBInput, Status304Header, status304_header_schema
from routes.schemas.generic_output import GenericOutput, generic_output_schema


def add_special_bp(app: APIFlask):
    log_debug("ROUTES", "Adding Special Blueprint")
    auth_if = get_auth_if(app)
    auth = auth_if.get_auth()
    special_bp = APIBlueprint("Special", __name__)


    @special_bp.get("/api/metrics")
    @special_bp.doc(summary="List Server Metrics", description="Fetch a Dict of various Metrics", tags=["Special"])
    @special_bp.output(list_metrics_output_schema)
    @special_bp.auth_required(auth, roles=[AuthRoles.RO])
    def get_metrics() -> ListMetricsOutput:
        metrics = {
            # app data
            "flask-title": app.title,
            "flask-version": app.version,
            # system data
            "os-ver": platform.platform(),
            "os-arch": platform.machine(),
            "os-uptime": str(dt.datetime.now() - dt.datetime.fromtimestamp(psutil.boot_time())),
            "os-cpu-load": psutil.cpu_percent(interval=1), # watch out - this is a blocking call
            "os-memory": psutil.virtual_memory().total,
            "os-memory-free": psutil.virtual_memory().free,
            "os-disk-usage": psutil.disk_usage("/").percent,
            "os-disk-total": psutil.disk_usage("/").total,
            "os-disk-free": psutil.disk_usage("/").free,
            "os-python-ver": platform.python_version(),
        }

        # fetch db metrics and append to dict
        db = get_db()
        metrics.update(db.get_metrics())

        return ListMetricsOutput(
            status="success",
            message="Metrics fetched successfully",
            data=metrics,
        )


    @special_bp.post("/api/branch/@me/import")
    @special_bp.doc(summary="Import Local DB", description="Import local database into User-Branch", tags=["Special"])
    @special_bp.input(existing_db_input_schema, location="json", arg_name="existing_db")
    @special_bp.output(generic_output_schema)
    @special_bp.auth_required(auth, roles=[AuthRoles.RW])
    def do_import(existing_db: ExistingDBInput) -> GenericOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        try:
            categories = parse_db(existing_db.category_db)
        except Exception as e:
            return ErrorResponse(ModelError(str(e)))

        # apply prefix
        for category in categories:
            category.name = existing_db.prefix + category.name

        # insert to db
        db = get_db()
        db.specials.batch_import(user.get_branch(), categories)

        return GenericOutput(
            status="success",
            message="Successfully imported local database",
        )

    @special_bp.get("/api/compile/<string:token_uuid>")
    @special_bp.doc(summary="Compile Local DB", description="Compile LocalDB for the provided Token", tags=["Special"])
    @special_bp.input(status304_header_schema, location='headers', arg_name="head")
    def handle_compile(token_uuid: str, head: Status304Header):
        # try to parse the "If-Modified-Since" header
        last_access_ts = None
        if head.if_modified_since is not None:
            try:
                # per spec this header is always utc. we unfortunately have to enforce this manually in python
                last_access = dt.datetime.strptime(head.if_modified_since, "%a, %d %b %Y %H:%M:%S GMT")
                last_access = last_access.replace(tzinfo=dt.timezone.utc)
                last_access_ts = last_access.timestamp()
            except ValueError:
                return (
                    "Invalid If-Modified-Since header",
                    400,
                    {"Content-Type": "text/plain"},
                )

        # ask model to parse localdb
        db = get_db()
        content, last_modified, error = db.specials.compile_localdb(token_uuid, last_access_ts)

        # convert last_modified to required UTC string (would default to local-timezone and not UTC)
        last_modified_dt = dt.datetime.fromtimestamp(last_modified, dt.timezone.utc)
        last_modified = last_modified_dt.strftime("%a, %d %b %Y %H:%M:%S GMT")

        # catch various "error" states
        if error == ERROR_NOT_FOUND:
            return (
                "Token not found",
                404,
                {"Content-Type": "text/plain"},
            )
        elif error == ERROR_UNCHANGED:
            return (
                "Not Modified",
                304,
                {
                    "Last-Modified": last_modified,
                    "Content-Type": "text/plain"
                }
            )
        elif error:
            return (
                "Error during compilation",
                500,
                {"Content-Type": "text/plain"},
            )

        return (
            content,
            200,
            {
                "Last-Modified": last_modified,
                "Content-Type": "text/plain"
            },
        )


    @special_bp.post("/api/branch/@me/cleanup")
    @special_bp.doc(summary="Cleanup User Branch", description="Cleanup Objects of a User's Branch", tags=["Special"])
    @special_bp.output(generic_output_schema)
    @special_bp.auth_required(auth, roles=[AuthRoles.RW])
    def handle_branch_cleanup() -> GenericOutput:
        user: AuthUser = cast(AuthUser, auth.current_user)

        db = get_db()
        db.specials.cleanup_unused(user.get_branch())

        return GenericOutput(
            status="success",
            message="Cleanup successful",
        )

    @special_bp.post("/api/cleanup-core")
    @special_bp.doc(summary="Cleanup Core Object", description="Cleanup central Core Object", tags=["Special"])
    @special_bp.output(generic_output_schema)
    @special_bp.auth_required(auth, roles=[AuthRoles.RW])
    def handle_core_cleanup() -> GenericOutput:
        db = get_db()
        db.specials.cleanup_core()

        return GenericOutput(
            status="success",
            message="Cleanup successful",
        )


    app.register_blueprint(special_bp)
