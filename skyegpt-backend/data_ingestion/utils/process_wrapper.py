import multiprocessing as mp

def create_process(target, args=()) -> mp.Process:
    return mp.Process(target=target,
                      args=args)

def start_process(process: mp.Process):
    process.start()

def join_process(process: mp.Process):
    process.join()