import argparse


def main():
    parser = argparse.ArgumentParser(description="Folder synchronizer")
    parser.add_argument("source", help="Path of the source folder")
    parser.add_argument("replica", help="Path of the replica folder")
    parser.add_argument("logfile", help="Path to the log file")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("comparison-algorithm", default="md5", help="Algorithm for comparison of checksum (md5, sha256...)")
    args = parser.parse_args()
    

if __name__ == "__main__":
    main()