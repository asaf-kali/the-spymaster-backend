from the_spymaster_solvers_client import TheSpymasterSolversClient

from the_spymaster.config import get_config

_client = None


def get_solvers_client():
    global _client
    if not _client:
        config = get_config()
        _client = TheSpymasterSolversClient(base_url=config.solvers_backend_url)
    return _client
