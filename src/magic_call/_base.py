import collections as _collections
from pathlib import Path as _Path
import shlex as _shlex
import shutil as _shutil
import subprocess as _subprocess
import tempfile as _tempfile

from . import _scheduler


# TODO: force formats to lowercase?


_BASENAME = 'magic_call'


class Caller:

    def __init__(self, commands=(), *, env=None, max_workers=None):
        """

        The order of *commands* matters!

        The "best" chain is not the one with the fewest stages,
        but the one that needs to go least far in the list of commands.

        Explicit tool chain can be specified: ``ps.pdf.png``, ``dvi.png``

        TODO: How to decide between ``pdf.svg`` and ``dvi.svg``?

        .. seealso::

            `example notebook`_

            .. _example notebook: caller.ipynb

        """
        self.commands = list(commands)
        self.env = env
        self.scheduler = _scheduler.Scheduler(max_workers)

    def call(self, source, formats=None, files=None, *, blocking=True):
        chains = self._formats2chains(formats, files)
        if isinstance(source, bytes):
            source_bytes = source
        else:
            source_bytes = source.encode()

        # TODO: make grouping more obvious? factor out?
        # Group by first format in chain (i.e. the "creator" format)
        groups = _collections.defaultdict(list)
        for i, chain in enumerate(chains):
            groups[chain[0]].append((i, chain[1:]))
        tasks = []
        indices = []  # Positions in the original list of formats
        for dst, numbered_chains in groups.items():
            idx, chains = zip(*numbered_chains)
            tasks.append((dst,  chains))
            indices.append(idx)

        nested_results = []
        for dst, chains in tasks:
            nested_results.append(
                    self._run_in_tempdir(source_bytes, dst, chains))

        results = []
        for idx, result in zip(indices, nested_results):
            results.extend(zip(idx, result))
        results.sort()  # Restore original order of formats
        results = [task for _, task in results]  # Undecorate

        # TODO: add_done_callback to cleanup() tempdir when all are done?

        if blocking:
            # Wait for futures
            results = [r.result() for r in results]

        number_of_formats = len(formats or ())
        format_results = results[:number_of_formats]
        file_results = results[number_of_formats:]

        if (formats, files) == (None, None):
            return None
        if files is None:
            return format_results
        if formats is None:
            return file_results
        return format_results, file_results

    def get_default_chains(self):
        """Populate dictionary of default tool chains by suffix.

        This works through the current list of *commands* to calculate
        the "best" tool chain for each possible suffix.

        """
        partial_chains = []
        chains = {}
        for name, command in self.commands:
            if '2' in name:
                src, _, dst = name.partition('2')
                if {src, dst} & {'', '.'}:
                    raise ValueError('Invalid command name: ' + repr(name))
            else:
                src, dst = '', name
            src = '.' + src
            dst = '.' + dst
            if dst in chains:
                pass  # There is already an earlier chain to create "dst"
            elif src == '.':
                # A "creator" that receives text and creates a file
                assert dst not in chains
                chains[dst] = [dst]
                old_partial_chains = partial_chains
                partial_chains = []
                for chain in old_partial_chains:
                    if chain[0] == dst:
                        if chain[-1] in chains:
                            continue  # There is already an earlier chain
                        # *Move* chain from old_partial_chains to chains
                        chains[chain[-1]] = chain
                    elif chain[-1] == dst:
                        # Current command is better than this partial chain
                        continue
                    else:
                        partial_chains.append(chain)
            elif src in chains:
                assert dst not in chains
                chains[dst] = chains[src] + [dst]
            else:
                partial_chains.append([src, dst])
                for chain in partial_chains.copy():
                    if chain[-1] == src:
                        partial_chains.append(chain + [dst])
                    if chain[0] == dst:
                        partial_chains.append([src] + chain)
        return chains

    def _run_in_tempdir(self, source_bytes, suffix, chains):
        # TODO: make sure tempdir gets cleaned up?
        # TODO: how do we know when moving files is finished?

        task_dir = self.scheduler.create_task(_create_temporary_directory)
        task_create = self.scheduler.create_task(
                self._create, source_bytes, task_dir,
                stem=_BASENAME, suffix=suffix)
        tasks = self._recurse_chains(task_create, suffix, chains)
        return [task.future for task in tasks]

    def _recurse_chains(self, source_task, suffix, chains):
        target_files = []
        decorated_tasks = []
        task_read = None

        # Group by first suffix in chain (for non-empty chains)
        groups = _collections.defaultdict(list)
        for i, chain in enumerate(chains):
            if not chain:
                if not task_read:
                    # TODO: more general mechanism to switch text/bytes
                    # Chain is finished, load data from file
                    if suffix == '.svg':
                        function = _read_text
                    else:
                        function = _read_bytes
                    task_read = self.scheduler.create_task(
                            function, source_task)
                # NB: There is only one task reading the file, but several
                # references to it might be appended to the results.
                decorated_tasks.append((i, task_read))
                continue
            if len(chain) == 1 and isinstance(chain[0], _Path):
                target_files.append(chain[0])
                continue
            groups[chain[0]].append((i, chain[1:]))

        tasks = []
        indices = []

        for dst, numbered_chains in groups.items():
            idx, chains = zip(*numbered_chains)
            tasks.append((dst, chains))
            indices.append(idx)

        if tasks:
            nested_results = []
            for dst, chains in tasks:
                converter_task = self.scheduler.create_task(
                        self._convert, source_task, suffix=dst)
                nested_results.append(
                        self._recurse_chains(converter_task, dst, chains))
            for idx, result in zip(indices, nested_results):
                decorated_tasks.extend(zip(idx, result))
            decorated_tasks.sort()  # Restore original order of chains

        data_tasks = [task for _, task in decorated_tasks]

        file_tasks = []
        # NB: All but the last file are copied ...
        for file in target_files[:-1]:
            file_tasks.append(self.scheduler.create_task(
                    _copy_file, source_task, path=file))
        # ... the last (and probably only) file can be moved.
        for file in target_files[-1:]:
            # NB: We are moving the file away, but we cannot do it before all
            # tasks in this stage are finished. So we add them as dependencies.
            file_tasks.append(self.scheduler.create_task(
                    _move_file, source_task, *data_tasks, *file_tasks,
                    path=file))
        return data_tasks + file_tasks

    def _formats2chains(self, formats, files):
        """Convert formats to full tool chains."""
        if isinstance(formats, str):
            raise TypeError('List of formats expected, not a single string')
        if isinstance(files, str):
            raise TypeError('List of file names expected, not a single string')
        # NB: Calling this every time is horribly inefficient, but the list of
        # commands is typically very short, so it doesn't take much time.
        default_chains = self.get_default_chains()

        def expand_chain(chain):
            first, chain = chain[0], chain[1:]
            try:
                prefix = default_chains[first]
            except KeyError:
                raise RuntimeError(
                    'No programs found to generate {!r} files'.format(first))
            return prefix + chain

        chains = []
        for format in formats or ():
            suffixes = ['.' + s for s in format.split('.')]
            if set(suffixes) & {'.'}:
                raise ValueError('Invalid format: ' + repr(format))
            chains.append(expand_chain(suffixes))
        for file in files or ():
            file = _Path(file)
            # Extract formats from given files
            suffixes = file.suffixes
            if not suffixes or set(suffixes) & {'.'}:
                raise ValueError('Invalid suffix in file: ' + repr(file.name))
            chains.append(expand_chain(suffixes + [file]))
        return chains

    def _get_command(self, name, *args):
        try:
            command = next(v for k, v in self.commands if k == name)
        except StopIteration:
            raise RuntimeError('Command not found: ' + name)
        return command.format(*args)

    def _create(self, task, source_bytes, tempdir):
        command = self._get_command(task.suffix[1:], task.stem)
        task.cwd = tempdir.path
        task.path = task.cwd / (task.stem + task.suffix)
        # TODO: use creationflags=0x08000000 on Windows (CREATE_NO_WINDOW)?
        process = _subprocess.run(
            _shlex.split(command),
            input=source_bytes,
            cwd=task.cwd,
            env=self.env,
            stdout=_subprocess.PIPE,
            stderr=_subprocess.STDOUT)
        if process.returncode or not task.path.is_file():
            raise RuntimeError('\n'.join([
                'Error running {!r} to create {!r} from this source:'.format(
                    command, str(task.path)),
                source_bytes.decode(),
                '#' * 80,
                process.stdout.decode(),
            ]))

    def _convert(self, task, source):
        # NB: The destination file has both suffixes!
        task.cwd = source.cwd
        task.path = source.path.with_suffix(source.suffix + task.suffix)
        command = self._get_command(
                source.suffix[1:] + '2' + task.suffix[1:],
                source.path, task.path)
        process = _subprocess.run(
            _shlex.split(command),
            cwd=task.cwd,
            env=self.env,
            stdout=_subprocess.PIPE,
            stderr=_subprocess.STDOUT)
        if process.returncode or not task.path.is_file():
            raise RuntimeError('\n'.join([
                'Error running {!r} to create {!r}:'.format(
                    command, task.path.name),
                process.stdout.decode(),
            ]))


def _create_temporary_directory(task):
    # TODO: cleanup() in the end?
    # NB: must be kept alive!
    task.tempdir = _tempfile.TemporaryDirectory(prefix=_BASENAME + '-')
    task.path = _Path(task.tempdir.name)


def _read_text(task, source):
    return source.path.read_text()


def _read_bytes(task, source):
    return source.path.read_bytes()


def _copy_file(task, source):
    # TODO: Exception might be raised on Windows if target file exists!?!
    _shutil.copy2(source.path, task.path)
    # NB: Exceptions are only shown if someone calls result() on this!
    return task.path


def _move_file(task, source, *dependencies):
    # TODO: Exception might be raised on Windows if target file exists!?!
    _shutil.move(source.path, task.path)
    # NB: Exceptions are only shown if someone calls result() on this!
    return task.path


def load_ipython_extension(ipython):
    """Hook function called by IPython."""
    # TODO: provide a list of all available sub-modules?
    from IPython.core.error import UsageError
    raise UsageError('Please use a specific sub-module, e.g.\n\n'
                     '    %load_ext magic_call.latex')
