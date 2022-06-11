from collections import defaultdict
from dataclasses import dataclass
from multiprocessing import Manager, Process
from threading import Thread
from typing import Iterable, Optional
from uuid import UUID, uuid4

_OPERATIONS = defaultdict(
    lambda: lambda _: None,
    {
        'sum': sum,
        'max': max,
        'min': min,
    },
)


@dataclass
class Task:
    id: UUID
    command: str
    sequence: Iterable[int]


def calculate(task: Task, storage) -> None:
    storage[task.id] = _OPERATIONS[task.command](task.sequence)


class Front(Process):
    def __init__(self, tasks_queue, storage) -> None:
        super().__init__()
        self.tasks_queue = tasks_queue
        self.storage = storage

    def call_command(self, command, sequence):
        task_id = uuid4()
        self.tasks_queue.put(Task(task_id, command, sequence))
        return task_id

    def get_result(self, task_id: UUID) -> Optional[int]:
        self.tasks_queue.join()
        return self.storage.pop(task_id)

    def run(self):
        pass


class Backend(Process):
    def __init__(self, tasks_queue, storage) -> None:
        super().__init__()
        self.tasks_queue = tasks_queue
        self.storage = storage

    def run(self) -> None:
        while not self.tasks_queue.empty():
            task = self.tasks_queue.get()
            thread = Thread(
                target=calculate,
                args=(
                    task,
                    self.storage,
                ),
            )
            thread.start()
            thread.join()
            self.tasks_queue.task_done()


class Composer:
    def __init__(self) -> None:
        manager = Manager()
        self.tasks_queue = manager.Queue()
        self.storage = manager.dict()
        self.backend = Backend(self.tasks_queue, self.storage)

    def start(self):
        self.backend.start()

    def stop(self):
        self.backend.join()
        self.front.join()

    def get_front(self):
        self.front = Front(self.tasks_queue, self.storage)
        self.front.start()
        return self.front


if __name__ == '__main__':
    composer = Composer()
    composer.start()
    front = composer.get_front()
    command_max = front.call_command('max', [1, 2, 3])
    command_min = front.call_command('min', [1, 2, 3])
    result_min = front.get_result(command_min)
    result_max = front.get_result(command_max)
    print(result_min)
    print(result_max)
    assert result_min == 1
    assert result_max == 3
    composer.stop()
