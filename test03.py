from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import time


class Task:
    pass


class Scheduler:

    # TODO: handle cancellations of futures?

    def __init__(self):
        #max_workers = 1
        max_workers = None
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def create_task(self, function, *dependencies, **kwargs):
        # NB: Using circular dependencies will cause deadlock!
        task = Task()
        for k, v in kwargs.items():
            setattr(task, k, v)
        task.future = self.executor.submit(
                _wrap_task, function, task, *dependencies)
        return task


def _wrap_task(function, task, *dependencies):
    # NB: waiting could be optional, but we want it all the time
    for dep in dependencies:
        # NB: This waits until all dependencies are done, but it also forces
        #     exceptions to show themselves (for easier debugging).
        dep.future.result()
    assert '_dependencies' not in kwargs
    task._dependencies = dependencies  # Keep dependencies alive
    return function(task, *dependencies)


def create_temporary_directory(task):
    print('creating temp dir')
    # NB: must be kept alive!
    task.tempdir = TemporaryDirectory(prefix='executor-test-')
    print('created temp dir', task.tempdir.name)
    task.path = Path(task.tempdir.name)


def create(task, tempdir):
    print('creating', task.suffix)
    time.sleep(3)
    task.cwd = tempdir.path
    task.path = task.cwd / (task.stem + task.suffix)
    with open(task.path, 'w') as f:
        f.write(task.suffix[1:] + ' content\n')
    print('created', task.suffix)


def convert(task, source):
    print('converting from', source.suffix, 'to', task.suffix)
    task.path = source.path.with_suffix(source.path.suffix + task.suffix)
    data = source.path.read_text()
    task.path.write_text(data + '... converted to {}'.format(task.suffix))
    time.sleep(1)
    print('finished converting from', source.suffix, 'to', task.suffix)


def get_data(task, source):
    print('reading from', source.path)
    time.sleep(3)
    if task.binary:
        return source.path.read_bytes()
    else:
        return source.path.read_text()


def move_file(task, source, *dependencies):
    print('moving file')
    dst = shutil.move(source.path, task.destination)
    print('moved file')
    # TODO: this error doesn't show up unless someone calls result() in the
    # main thread!
    raise RuntimeError('error')
    return dst
    # TODO: how to catch errors if future is never queried?


#class Cleanup:
#
#    def run(self, tempdir, *dependencies):
#        print('starting cleanup')
#        tempdir.tempdir.cleanup()
#        print('cleanup done')


# Test to check if temp dir is kept alive
def get_only_futures(sched):
    sched = Scheduler()
    task_dir = sched.create_task(create_temporary_directory)
    task_dvi = sched.create_task(create, task_dir, stem='myfile', suffix='.dvi')
    task_ps = sched.create_task(convert, task_dvi, suffix='.ps')
    task_pdf = sched.create_task(convert, task_ps, suffix='.pdf')
    task_svg = sched.create_task(convert, task_dvi, suffix='.svg')
    task_svg_data = sched.create_task(get_data, task_svg, binary=False)
    task_ps_data = sched.create_task(get_data, task_ps)
    task_move_svg = sched.create_task(
            move_file, task_svg, task_svg_data, destination='delme.svg')

    #task_cleanup = Cleanup()
    #sched.create_task(task_cleanup, task_dir, task_ps_data, task_svg_data,
    #               task_pdf, task_move_svg)

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
