"""
File watcher that automatically indexes new files and deletes removed files.
"""
import os
import time
from pathlib import Path
from typing import List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from llama_index.core import SimpleDirectoryReader

class FileChangeHandler(FileSystemEventHandler):
    """
    Handles file system events to automatically update the vector store.
    """

    def __init__(self, vector_store_manager, exclude_list: List[str], data_dir: str):
        """
        Initializes the FileChangeHandler.

        Args:
            vector_store_manager (VectorStoreManager): The manager for the vector store.
            exclude_list (List[str]): List of glob patterns to exclude.
            data_dir (str): The directory being watched.
        """
        self.vector_store_manager = vector_store_manager
        self.exclude_list = exclude_list
        self.data_dir = data_dir

    def on_created(self, event):
        """
        Called when a file or directory is created.

        Args:
            event (FileSystemEvent): The event representing the file/directory creation.
        """
        if not event.is_directory:
            if not os.path.exists(event.src_path):
                print(f"File {event.src_path} not found, skipping.")
                return

            src_path = Path(event.src_path)

            # Check if the file is hidden
            try:
                relative_path = src_path.relative_to(self.data_dir)
                if any(part.startswith('.') for part in relative_path.parts):
                    print(f"Excluding hidden file: {event.src_path}")
                    return
            except ValueError:
                # This can happen if the file is not in the data_dir, which shouldn't happen
                pass
            
            print(f"New file detected: {event.src_path}")
            # Check if the file should be excluded by other patterns
            for pattern in self.exclude_list:
                if src_path.match(pattern):
                    print(f"Excluding {event.src_path} based on pattern {pattern}")
                    return
            
            try:
                new_docs = SimpleDirectoryReader(input_files=[event.src_path]).load_data()
                self.vector_store_manager.add_documents(new_docs)
            except Exception as e:
                print(f"Error processing new file {event.src_path}: {e}")

def start_watching(data_dir: str, vector_store_manager, exclude_list: List[str]):
    """
    Starts watching the specified directory for file changes.

    Args:
        data_dir (str): The directory to watch.
        vector_store_manager (VectorStoreManager): The manager for the vector store.
        exclude_list (List[str]): List of glob patterns to exclude.
    """
    event_handler = FileChangeHandler(vector_store_manager, exclude_list, data_dir)
    observer = Observer()
    observer.schedule(event_handler, data_dir, recursive=True)
    observer.start()
    print(f"Watching for file changes in {data_dir}...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
