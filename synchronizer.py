import argparse
import os
import shutil

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
    
    def sync(self):
        # TODO's:
        # Check if is the replica file up to date / different. And update if needed.
        # Implement logging


        for root, dirs, files in os.walk(self.source):
            """ Updates folder structure in replica based on source """
            replica_dir = os.path.join(self.replica, os.path.relpath(root, self.source))
            os.makedirs(replica_dir, exist_ok=True)

            for file in files:
                source_file = os.path.join(root, file)
                replica_file = os.path.join(replica_dir, file)

                if not os.path.exists(replica_file):
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
        # TODO's:
        # Add implicit wait.

        sync.sync()

if __name__ == "__main__":
    main()

# python synchronizer.py "C:\Users\Z0045DVA\Documents\veeam\source", "C:\Users\Z0045DVA\Documents\veeam\replica", "C:\Users\Z0045DVA\Documents\veeam\replica", 5, "md5"