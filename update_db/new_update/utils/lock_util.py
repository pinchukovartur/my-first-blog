import os

# lock file path
__lock_file_path__ = os.path.dirname(os.path.realpath(__file__)) + "/lock.app"


# The method create lock file
def start_work():
    if os.path.isfile(__lock_file_path__):
        raise NameError("start work: found lock file")
    else:
        file = open(__lock_file_path__, "w")
        file.write("this file auto generate")
        file.close()


# The method delete lock file
def end_work():
    if os.path.isfile(__lock_file_path__):
        os.remove(__lock_file_path__)
    else:
        raise NameError("end work: not found lock file")
