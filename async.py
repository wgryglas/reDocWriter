
import threading
import subprocess


def start_process(onSuccess, onError, cwd, commands):
    """
    Runs the given args in a subprocess.Popen, and then calls the function
    onExit when the subprocess completes.
    onExit is a callable object, and popenArgs is a list/tuple of args that
    would give to subprocess.Popen.

    Note:
    StackOverflow copy - in my opinion it is risky solution, as onExit will be
    called in the new thread, not the one function popenAndCall

    """
    def runInThread(onSuccess, onError, cwd, commands):
        proc = subprocess.Popen(commands, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        std, err = proc.communicate()
        if proc.returncode == 0:
            onSuccess(std)
        else:
            if not err:
                onError("Unknown error")
            else:
                onError(str(err))
        return

    thread = threading.Thread(target=runInThread, args=(onSuccess, onError, cwd, commands))
    thread.start()
    # returns immediately after the thread starts
    return thread
