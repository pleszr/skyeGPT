"""Utility functions for creating, starting, and joining multiprocessing processes."""

import multiprocessing as mp


def create_process(target, args=()) -> mp.Process:
    """Create a multiprocessing Process for the given target and arguments."""
    return mp.Process(target=target, args=args)


def start_process(process: mp.Process):
    """Start the given multiprocessing Process."""
    process.start()


def join_process(process: mp.Process):
    """Wait for the given multiprocessing Process to complete."""
    process.join()
