from collections import defaultdict
from dataclasses import dataclass
from multiprocessing import Process, Queue
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


def calculate(task: Task, results_queue: Queue) -> None:
    results_queue.put([task.id, _OPERATIONS[task.command](task.sequence)])


def process_backend(tasks_queue: Queue, results_queue: Queue) -> None:
    while True:
        task = tasks_queue.get()
        if task is None:
            break

        thread = Thread(
            target=calculate,
            args=(
                task,
                results_queue,
            ),
        )
        thread.start()
        thread.join()


def process_fronted(tasks_queue, results_queue):
    return


class Worker:
    def __init__(self, tasks_queue: Queue, results_queue: Queue) -> None:
        self.tasks_queue = tasks_queue
        self.results_queue = results_queue

    def start(self):
        self.process.start()

    def stop(self):
        self.tasks_queue.put(None)


class Front(Worker):
    def __init__(self, tasks_queue: Queue, results_queue: Queue) -> None:
        super().__init__(tasks_queue, results_queue)
        self.storage = {}
        self.process = Process(
            target=process_fronted, args=(self.results_queue, self.storage)
        )

    def call_command(self, command: str, sequence: Iterable[int]) -> UUID:
        task_id = uuid4()
        self.tasks_queue.put(Task(task_id, command, sequence))
        return task_id

    def get_result(self, task_id: UUID) -> Optional[int]:
        if task_id in self.storage:
            return self.storage.pop(task_id)

        id_, result = self.results_queue.get()
        if id_ == task_id:
            return result

        self.storage[id_] = result
        return self.get_result(task_id)


class Backend(Worker):
    def __init__(self, tasks_queue, results_queue) -> None:
        super().__init__(tasks_queue, results_queue)
        self.process = Process(
            target=process_backend, args=(self.tasks_queue, self.results_queue)
        )


class Composer:
    def __init__(self) -> None:
        self.tasks_queue = Queue()
        self.results_queue = Queue()
        self.backend = Backend(self.tasks_queue, self.results_queue)
        self.frontend = Front(self.tasks_queue, self.results_queue)

    def start(self):
        self.backend.start()
        self.frontend.start()

    def stop(self):
        self.backend.stop()
        self.frontend.stop()

    def get_front(self):
        return self.frontend


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
