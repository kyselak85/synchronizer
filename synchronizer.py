
import argparse
import os
import shutil
import hashlib
import time
import logging


class Synchronizer:
    """
    Synchronizes replica folder and source folder based on comparison algorithm.
    Synchronization is only one-way
    Changes in replica are not reflected in source.
    """

    def __init__(self, source, replica, logfile, interval, algorithm="md5"):
        self.source = source
        self.replica = replica
        self.logfile = logfile
        self.interval = interval
        self.algorithm = algorithm.lower() # Ensure algorithm name is lowercase

        if self.algorithm not in hashlib.algorithms_available:
            logging.error(f"Chosen algorithm {self.algorithm} not available")
            raise ValueError(f"Invalid checksum algorithm: {self.algorithm}")

    def get_checksum(self, filepath):
        """ Calculates a checksum of a file using the specified algorithm.

        Args:
            filepath: Path to the file for which is checksum created.
        """
        with open(filepath, 'rb') as f:
            data = f.read()
            return getattr(hashlib, self.algorithm)(data).hexdigest()
    
    def create_replica_folder(self, source_dir, replica_dir):
        """Creates the folder structure in the replica based on the source directory.

        Args:
            source_dir: Path to the source directory.
            replica_dir: Path to the corresponding directory in the replica.
        """
        os.makedirs(replica_dir, exist_ok=True)

    def delete_extra_replica_items(self, replica_dir, items):
        """Deletes files and directories in the replica that are not present in the source.

        Args:
            replica_dir: Path to the directory in the replica.
            items: List of files and directories in the source directory.
        """
        for item in os.listdir(replica_dir):
            replica_item = os.path.join(replica_dir, item)
            if os.path.isfile(replica_item) and item not in items:
                os.remove(replica_item)
                logging.info(f"Deleted: {replica_item}")
            elif os.path.isdir(replica_item) and item not in items:
                shutil.rmtree(replica_item)
                logging.info(f"Deleted: {replica_dir}")

    def copy_missing_files(self, source_dir, replica_dir, files):
        """Copies files from the source directory to the replica if they are missing.

        Args:
            source_dir: Path to the source directory.
            replica_dir: Path to the corresponding directory in the replica.
            files: List of files in the source directory.
        """
        for file in files:
            source_file = os.path.join(source_dir, file)
            replica_file = os.path.join(replica_dir, file)
            if not os.path.exists(replica_file):
                shutil.copy(source_file, replica_file)
                logging.info(f"Created: {replica_file}")

    def update_changed_files(self, source_file, replica_file):
        """Checks if the source file has changed and updates the replica if needed.

        Args:
            source_file: Path to the source file.
            replica_file: Path to the corresponding file in the replica.
        """
        source_checksum = self.get_checksum(source_file)
        replica_checksum = self.get_checksum(replica_file)
        if source_checksum != replica_checksum:
            os.remove(replica_file)
            shutil.copy(source_file, replica_file)
            logging.info(f"""Updated: {source_file} -> {replica_file}""")
    
    def sync(self):
        """
        Synchronizes replica folder and source folder.

        This function performs the following actions:
            1. Creates the folder structure in the replica to match the source.
            2. Deletes any files or directories in the replica that are not present in the source.
            3. Copies any files missing from the replica from the source.
            4. Updates the replica if the source file has changed.
        """
        logging.info(f"Synchronization started")

        for root, dirs, files in os.walk(self.source):
            replica_dir = os.path.join(self.replica, os.path.relpath(root, self.source))
            self.create_replica_folder(root, replica_dir)
            self.delete_extra_replica_items(replica_dir, items=dirs + files)
            self.copy_missing_files(root, replica_dir, files)
            # Update modified files
            for file in files:
                source_file = os.path.join(root, file)
                replica_file = os.path.join(replica_dir, file)
                self.update_changed_files(source_file, replica_file)


def main():
    parser = argparse.ArgumentParser(description="Folder synchronizer")
    parser.add_argument("source", default="tmp/source",
                        help="Path of the source folder")
    parser.add_argument("replica", default="tmp/replica",
                        help="Path of the replica folder")
    parser.add_argument("logfile", default="tmp/logfile.log",
                        help="Path to the log file")
    parser.add_argument("interval", default=300, type=int, 
                        help="Synchronization interval in seconds")
    parser.add_argument("algorithm", default="md5",
                        help="Algorithm for comparison of checksums")
    args = parser.parse_args()
    
    # Initialization of Synchronizer.
    sync = Synchronizer(args.source, args.replica, args.logfile, 
                        args.interval, args.algorithm)

    #Configuration of logging.
    logging.basicConfig(filename=args.logfile, 
                        format='%(asctime)s %(levelname)s %(message)s', 
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)
    
    # Run synchronization and wait defined time to next synchronization.
    while True:
        sync.sync()
        time.sleep(args.interval)


if __name__ == "__main__":
    main()

# python synchronizer.py "C:\Users\Z0045DVA\Documents\veeam\source", "C:\Users\Z0045DVA\Documents\veeam\replica", "C:\Temp\logfile.log", 5, "md5"