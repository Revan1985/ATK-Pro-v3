import time
from PySide6.QtCore import QObject, QThread, Signal, Slot


class Worker(QObject):
    finished = Signal()

    def __init__(self):
        super().__init__()
        self._running = True

    @Slot()
    def run(self):
        # Simple loop that exits when _running is False
        while self._running:
            QThread.msleep(10)
        self.finished.emit()

    @Slot()
    def stop(self):
        self._running = False


def test_worker_shutdown_finishes_cleanly():
    thread = QThread()
    worker = Worker()
    worker.moveToThread(thread)

    # connect start and finish
    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)

    thread.start()
    # let it run briefly
    time.sleep(0.05)

    # request stop from worker thread using a queued call
    # calling stop directly is okay because it's thread-safe here
    worker.stop()

    # ensure thread quits and finishes within timeout
    thread.quit()
    finished = thread.wait(2000)
    assert finished is True
    assert not thread.isRunning()
