
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
            raise ValueError(f"Invalid checksum algorithm: {algorithm}")

    def get_checksum(self, filepath):
        """ Calculates a checksum of a file using the specified algorithm."""
        with open(filepath, 'rb') as f:
            data = f.read()
            return getattr(hashlib, self.algorithm)(data).hexdigest()
    
    def sync(self):
        logging.info(f"Synchronization started")

        try:
            for root, dirs, files in os.walk(self.source):
                """ Updates folder structure in replica based on source. """
                replica_dir = os.path.join(self.replica, os.path.relpath(root, self.source))
                os.makedirs(replica_dir, exist_ok=True)

                for item in os.listdir(replica_dir):
                    replica_item = os.path.join(replica_dir, item)

                    # Delete files which are in the replica but not in the source
                    if os.path.isfile(replica_item) and item not in files:
                        os.remove(replica_item)
                        logging.info(f"Deleted: {replica_item}")

                    # Delete dirs which are in the replica but not in the source
                    elif os.path.isdir(replica_item) and item not in dirs:
                        shutil.rmtree(replica_item)
                        logging.info(f"Deleted: {replica_item}")

                for file in files:
                    source_file = os.path.join(root, file)
                    replica_file = os.path.join(replica_dir, file)

                    # Copy source files which are not in replica
                    if not os.path.exists(replica_file):
                        shutil.copy(source_file, replica_file)
                        logging.info(f"Created: {replica_file}")

                    else:
                        # Check if files need update based on checksum
                        source_checksum = self.get_checksum(source_file)
                        replica_checksum = self.get_checksum(replica_file)
                        if source_checksum != replica_checksum:
                            os.remove(replica_file)
                            shutil.copy(source_file, replica_file)
                            logging.info(f"""Updated: {source_file} -> {replica_file}""")

            logging.info(f"""Synchronization complete. Sleeping for {self.interval} seconds.""")
        
        except Exception as e:
            logging.error(f"Synchronization failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Folder synchronizer")
    parser.add_argument("source", default="tmp/source",
                        help="Path of the source folder")
    parser.add_argument("replica", default="tmp/replica",
                        help="Path of the replica folder")
    parser.add_argument("logfile", 
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