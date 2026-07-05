from app.bootstrap.application import setup_application
from app.infrastructure.http.server.config import server_config
from app.infrastructure.http.server.start_server import start_server_with_setup


def main():
    app = setup_application()

    start_server_with_setup(server_config, app)


if __name__ == '__main__':
    main()
