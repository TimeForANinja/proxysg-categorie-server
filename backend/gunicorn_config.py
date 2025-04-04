from app import initialize_app, app

def on_starting(server):
    # Call initialize_app to trigger background tasks scheduler
    # this will only get called for the master worker
    initialize_app(app)
