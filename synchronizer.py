import argparse
import os
import shutil
import hashlib
import time

class Synchronizer:
    """
    Synchronizes replica folder with a source folder based on the choosen comparison algorithm.
    Synchronization is only one-way, therefore changes in replica are not repflected in source.
    """

    def __init__(self, source, replica, logfile, algorithm):
        self.source = source
        self.replica = replica
        self.logfile = logfile
        self.algorithm = algorithm

    def get_checksum(self, filepath):
        """ Calculates a checksum of a file using the specified algorithm."""
        with open(filepath, 'rb') as f:
            data = f.read()
            return getattr(hashlib, self.algorithm)(data).hexdigest()
    
    def sync(self):
        # TODO's:
        # Implement logging

        for root, dirs, files in os.walk(self.source):
            """ Updates folder structure in replica based on source. """
            replica_dir = os.path.join(self.replica, os.path.relpath(root, self.source))
            os.makedirs(replica_dir, exist_ok=True)

            for file in files:
                source_file = os.path.join(root, file)
                replica_file = os.path.join(replica_dir, file)

                # Copy source files which are not in replica
                if not os.path.exists(replica_file):
                    shutil.copy(source_file, replica_file)
                
                else:
                    # Check if files need update based on checksum
                    source_checksum = self.get_checksum(source_file)
                    replica_checksum = self.get_checksum(replica_file)
                    if source_checksum != replica_checksum:
                        os.remove(replica_file)
                        shutil.copy(source_file, replica_file)

                if not os.path.exists(source_file):
                    os.remove(replica_file)

def main():

    parser = argparse.ArgumentParser(description="Folder synchronizer")
    parser.add_argument("source", help="Path of the source folder")
    parser.add_argument("replica", help="Path of the replica folder")
    parser.add_argument("logfile", help="Path to the log file")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("algorithm", default="md5", help="Algorithm for comparison of checksum (md5, sha256...)")
    args = parser.parse_args()
    
    sync = Synchronizer(args.source, args.replica, args.logfile, args.algorithm)

    while True:
        sync.sync()
        time.sleep(args.interval)

if __name__ == "__main__":
    main()

# python synchronizer.py "C:\Users\Z0045DVA\Documents\veeam\source", "C:\Users\Z0045DVA\Documents\veeam\replica", "C:\Users\Z0045DVA\Documents\veeam\replica", 5, "md5"