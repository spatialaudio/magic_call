from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import time


class Scheduler:

    # TODO: handle cancellations of futures?

    def __init__(self):
        #max_workers = 1
        max_workers = None
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def add_task(self, task, *dependencies, **kwargs):
        # NB: Using circular dependencies will cause deadlock!
        assert not hasattr(task, 'future')
        task.future = self.executor.submit(
                _wrap_task, task, *dependencies, **kwargs)
        return task


def _wrap_task(task, *dependencies, **kwargs):
    # NB: waiting could be optional, but we want it all the time
    for dep in dependencies:
        # NB: This waits until all dependencies are done, but it also forces
        #     exceptions to show themselves (for easier debugging).
        dep.future.result()
    task._dependencies = dependencies  # Keep dependencies alive
    return task.run(*dependencies, **kwargs)


class CreateTemporaryDirectory:

    def run(self):
        print('creating temp dir')
        # NB: must be kept alive!
        self.tempdir = TemporaryDirectory(prefix='executor-test-')
        print('created temp dir', self.tempdir.name)
        self.path = Path(self.tempdir.name)


class Create:

    def __init__(self, stem, suffix):
        self.stem = stem
        self.suffix = suffix

    def run(self, tempdir):
        print('creating', self.suffix)
        time.sleep(3)
        self.cwd = tempdir.path
        self.path = self.cwd / (self.stem + self.suffix)
        with open(self.path, 'w') as f:
            f.write(self.suffix[1:] + ' content\n')
        print('created', self.suffix)


class Convert:

    def __init__(self, suffix):
        self.suffix = suffix

    def run(self, source):
        print('converting from', source.suffix, 'to', self.suffix)
        self.path = source.path.with_suffix(source.path.suffix + self.suffix)
        data = source.path.read_text()
        self.path.write_text(data + '... converted to {}'.format(self.suffix))
        time.sleep(1)
        print('finished converting from', source.suffix, 'to', self.suffix)


class GetData:

    def __init__(self, binary=True):
        self.binary = binary

    def run(self, source):
        print('reading from', source.path)
        time.sleep(3)
        if self.binary:
            return source.path.read_bytes()
        else:
            return source.path.read_text()


class MoveFile:

    def __init__(self, destination):
        self.destination = destination

    def run(self, source, *dependencies):
        print('moving file')
        dst = shutil.move(source.path, self.destination)
        print('moved file')
        # TODO: this error doesn't show up unless someone calls result() in the
        # main thread!
        raise RuntimeError('error')
        return dst
        # TODO: how to catch errors if future is never queried?


class Cleanup:

    def run(self, tempdir, *dependencies):
        print('starting cleanup')
        tempdir.tempdir.cleanup()
        print('cleanup done')


# Test to check if temp dir is kept alive
def get_only_futures(sched):
    sched = Scheduler()
    task_dir = sched.add_task(CreateTemporaryDirectory())
    task_dvi = sched.add_task(Create('myfile', '.dvi'), task_dir)
    task_ps = sched.add_task(Convert('.ps'), task_dvi)
    task_pdf = sched.add_task(Convert('.pdf'), task_ps)
    task_svg = sched.add_task(Convert('.svg'), task_dvi)
    task_svg_data = sched.add_task(GetData(binary=False), task_svg)
    task_ps_data = sched.add_task(GetData(), task_ps)

    task_move_svg = MoveFile('delme.svg')
    sched.add_task(task_move_svg, task_svg, task_svg_data)

    task_cleanup = Cleanup()
    sched.add_task(task_cleanup, task_dir, task_ps_data, task_svg_data,
                   task_pdf, task_move_svg)

    #task_move_svg.future.result()

    #task_cleanup.future.result()

    # waits for all to be finished
    #sched.executor.shutdown()

    return task_svg_data.future, task_ps_data.future
    #return task_svg_data.future, task_ps_data.future, task_cleanup.future


if __name__ == '__main__':
    sched = 'dummy'

    futures = get_only_futures(sched)

    #print('Press return to continue ...')
    #input()  # check out the temp dir, then close

    for f in futures:
        print(repr(f.result()))

    time.sleep(10)
