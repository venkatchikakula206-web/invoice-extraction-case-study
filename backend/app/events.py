import queue
from collections import defaultdict

# doc_id -> list[queue.Queue]
_subscribers: dict[int, list[queue.Queue]] = defaultdict(list)

def subscribe(doc_id: int) -> queue.Queue:
    q: queue.Queue = queue.Queue()
    _subscribers[doc_id].append(q)
    return q

def publish(doc_id: int, event: dict):
    for q in list(_subscribers.get(doc_id, [])):
        try:
            q.put_nowait(event)
        except Exception:
            pass

def unsubscribe(doc_id: int, q: queue.Queue):
    if doc_id in _subscribers and q in _subscribers[doc_id]:
        _subscribers[doc_id].remove(q)
        if not _subscribers[doc_id]:
            _subscribers.pop(doc_id, None)
