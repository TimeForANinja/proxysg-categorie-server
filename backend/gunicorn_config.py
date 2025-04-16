from app import initialize_app, app

def on_starting():
    # Call initialize_app to trigger background tasks scheduler
    # this will only get called for the master worker
    initialize_app(app)
