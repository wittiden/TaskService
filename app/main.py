from app.bootstrap.application import setup_app
from app.common.limiter.limit import limiter

from app.infrastructure.http.server.config import server_config
from app.infrastructure.http.server.start_server import start_server_with_setup

def main() -> None:

    app = setup_app()

    app.state.limiter = limiter

    start_server_with_setup(server_config, app)


if __name__ == '__main__':
    main()
