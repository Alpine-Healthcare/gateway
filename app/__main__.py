import uvicorn

from app.gunicorn_runner import GunicornApplication
from app.settings import settings
import pyroscope
import ssl

pyroscope.configure(
  application_name = "com.alpine.sherpa", # replace this with some name for your application
  server_address   = "http://my-pyroscope-server:4040", # replace this with the address of your Pyroscope server
)

def main() -> None:

    is_production = settings.environment == "production"


    """Entrypoint of the application."""
    if settings.reload:
        uvicorn.run(
            "app.web.application:get_app",
            workers=settings.workers_count,
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=settings.log_level.value.lower(),
            factory=True,
            ssl_certfile="./cert.pem" if is_production else None,
            ssl_keyfile="./key.pem" if is_production else None,
        )
    else:
        # We choose gunicorn only if reload
        # option is not used, because reload
        # feature doen't work with Uvicorn workers.
        GunicornApplication(
            "app.web.application:get_app",
            host=settings.host,
            port=settings.port,
            workers=settings.workers_count,
            factory=True,
            accesslog="-",
            loglevel=settings.log_level.value.lower(),
            access_log_format='%r "-" %s "-" %Tf',  # noqa: WPS323
        ).run()


if __name__ == "__main__":
    main()
