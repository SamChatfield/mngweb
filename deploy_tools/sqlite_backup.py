import argparse
import sqlite3
import shutil
import time
import os


def sqlite3_safe_copy(db_path, backup_dir):
    """Create timestamped database copy"""
    if not os.path.isdir(backup_dir):
        raise Exception("Backup directory does not exist: {}".format(backup_dir))
    backup_path = os.path.join(backup_dir, os.path.basename(db_path) + time.strftime("-%Y%m%d-%H%M%S"))
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Lock db, copy, release
    cur.execute('begin immediate')
    shutil.copyfile(db_path, backup_path)
    con.rollback()
    con.close()


def delete_stale_backups(backup_dir, days_to_keep):
    """Delete stale backup files, older than days to keep"""
    for f in os.listdir(backup_dir):
        path = os.path.join(backup_dir, f)
        if os.path.isfile(path) and os.stat(path).st_ctime < (time.time() - days_to_keep * 86400):
            os.remove(path)


def get_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Create a timestamped backup of a SQLite db; delete stale copies from backup dir")
    parser.add_argument('db_path', help="Database file path")
    parser.add_argument('backup_dir', help="Backup directory path")
    parser.add_argument('--days-to-keep', type=int, default=7, help="N days to keep backup copies")
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    print("Creating db copy...")
    sqlite3_safe_copy(args.db_path, args.backup_dir)
    print("Removing stale backups...")
    delete_stale_backups(args.backup_dir, args.days_to_keep)
    print("Backup complete")
