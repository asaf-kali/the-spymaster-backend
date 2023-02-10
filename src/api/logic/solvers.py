from functools import lru_cache

from the_spymaster_solvers_client import TheSpymasterSolversClient

from the_spymaster.config import get_config


@lru_cache()
def get_solvers_client():
    config = get_config()
    return TheSpymasterSolversClient(base_url=config.solvers_backend_url)
