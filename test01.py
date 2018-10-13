from concurrent.futures import ThreadPoolExecutor
import contextlib
import threading
import time


# TODO: create temp dir asynchronously?


def make_svg(pdf_fut):
    print('waiting for svg')
    pdf_data, tempdir = pdf_fut.result()
    print('starting svg')
    time.sleep(5)
    print('finished svg')
    return pdf_data + '-svg'


def make_png(pdf_fut):
    print('waiting for png')
    pdf_data, tempdir = pdf_fut.result()
    print('starting png')
    time.sleep(3)
    print('finished png')
    return pdf_data + '-png'


class TemporaryDirectory:

    _semaphore = None

    def __init__(self):
        self._lock = threading.Lock()
        self._path = ''  # TODO: use pathlib?

    @contextlib.contextmanager
    def create(self):
        with self._lock:
            assert self._path == ''
            print('starting to create temp dir')
            time.sleep(2)
            print('finished creating temp dir')
            self._path = '/tmp/123'
        return self._path

    def _destroy(self):
        with self._lock:
            tempdir = self._path
            self._path = ''
        if tempdir:
            print('starting to destroy temp dir', tempdir)
            time.sleep(4)
            print('finished destroying temp dir')
        else:
            print('not destroying')

    def make_done_callback(self):
        # We need to call release() one fewer times than there are callbacks
        if not self._semaphore:
            self._semaphore = threading.Semaphore(0)
        else:
            self._semaphore.release()

        def callback(future):
            if self._semaphore.acquire(blocking=False):
                print('*not* cleaning up')
            else:
                # TODO: do something with "future"? check for exception?
                self._destroy()

        return callback


# TODO: cancellation of futures?


def run_latex(arg, tempdir):
    path = tempdir.create()
    print('starting latex')
    time.sleep(4)
    print('finished latex')
    pdf_data = arg
    return pdf_data, path


def run_chain(data, executor):
    tempdir = TemporaryDirectory()
    pdf_fut = executor.submit(run_latex, data, tempdir)
    pdf_fut.add_done_callback(tempdir.make_done_callback())
    futures = [
        executor.submit(make_svg, pdf_fut),
        executor.submit(make_png, pdf_fut),
    ]
    print('done submitting')
    for fut in futures:
        fut.add_done_callback(tempdir.make_done_callback())
    print('done setting callback')
    return futures


if __name__ == '__main__':
    executor = ThreadPoolExecutor(max_workers=1)
    #executor = ThreadPoolExecutor()
    list_of_fut = run_chain('data2', executor)
    print('list of futures came in')
    #for fut in reversed(list_of_fut):
    for fut in list_of_fut:
        print(fut.result())
    print('I got everything!')
