from dotenv import load_dotenv
load_dotenv()

from . import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    settings = app.config["SETTINGS"]
    app.run(host=settings.app_host, port=settings.app_port, debug=True, threaded=True)
