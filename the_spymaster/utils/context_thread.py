import threading
from typing import Any, Callable, Iterable, Mapping, Optional

from the_spymaster.utils import get_logger

log = get_logger(__name__)


# Hacky way to make all threads inherit log context from theirs creating thread


def _make_target_context_aware(target: Optional[Callable], parent_context: dict) -> Optional[Callable]:
    if not target:
        return None

    def wrapper(*args, **kwargs):
        try:
            log.update_context(**parent_context)
        except:  # noqa
            pass
        return target(*args, **kwargs)

    return wrapper


_original_thread_init = threading.Thread.__init__  # type: ignore


def context_aware_init(  # noqa
    self,
    group=None,
    target: Optional[Callable] = None,
    name: Optional[str] = None,
    args: Iterable[Any] = None,
    daemon: bool = False,
    kwargs: Optional[Mapping[str, Any]] = None,
):
    context_aware_target = _make_target_context_aware(target=target, parent_context=log.context)
    _original_thread_init(
        self, group=group, target=context_aware_target, name=name, args=args or [], kwargs=kwargs, daemon=daemon
    )


threading.Thread.__init__ = context_aware_init  # type: ignore
