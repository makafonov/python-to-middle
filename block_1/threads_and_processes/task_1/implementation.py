from abc import ABC
from abc import abstractstaticmethod
from collections import defaultdict
from dataclasses import dataclass
from multiprocessing import Process
from multiprocessing import Queue
from threading import Thread
from typing import Iterable
from typing import Optional
from uuid import UUID
from uuid import uuid4


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


def calculate(task: Task, results: Queue) -> None:
    results.put([task.id, _OPERATIONS[task.command](task.sequence)])


class Worker(ABC):
    def __init__(self, tasks: Queue, results: Queue) -> None:
        self.worker: Process
        self.tasks = tasks
        self.results = results

    def start(self):
        self.worker.start()

    def stop(self):
        self.worker.terminate()
        self.worker.join()

    @abstractstaticmethod
    def _run():
        pass


class Front(Worker):
    def __init__(self, tasks: Queue, results: Queue) -> None:
        super().__init__(tasks, results)
        self.messages = Queue()
        self.storage = {}
        self.worker = Process(
            target=self._run, args=(self.messages, self.tasks)
        )

    def get_result(self, task_id: UUID) -> Optional[int]:
        if task_id in self.storage:
            return self.storage.pop(task_id)

        id_, result = self.results.get()
        if id_ == task_id:
            return result

        self.storage[id_] = result
        return self.get_result(task_id)

    def call_command(self, command: str, sequence: Iterable[int]) -> UUID:
        task_id = uuid4()
        self.messages.put(Task(task_id, command, sequence))
        return task_id

    @staticmethod
    def _run(messages: Queue, tasks: Queue):
        while True:
            message = messages.get()
            if message:
                tasks.put(message)


class Back(Worker):
    def __init__(self, tasks: Queue, results: Queue) -> None:
        super().__init__(tasks, results)
        self.worker = Process(
            target=self._run, args=(self.tasks, self.results)
        )

    @staticmethod
    def _run(tasks: Queue, results: Queue) -> None:
        while True:
            task = tasks.get()
            thread = Thread(target=calculate, args=(task, results))
            thread.start()
            thread.join()


class Composer:
    def __init__(self) -> None:
        self._tasks = Queue()
        self._results = Queue()
        self._front = Front(self._tasks, self._results)
        self._back = Back(self._tasks, self._results)

    def start(self):
        self._back.start()
        self._front.start()

    def stop(self):
        self._front.stop()
        self._back.stop()

    def get_front(self):
        return self._front


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
