import sqlite3
from sqlite3 import Error
from mriqa import directory_score
from timer import Timer
from prettytable import PrettyTable, from_db_cursor
import argparse
import os
import math
 
row = ["directory", "img_quality_score", "img_slice_score", "weighted_score", "total_slice", "elapsed time"]

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        # create and connect the created database 
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn

def create_table(conn):
    sql_create_mri_table = """ CREATE TABLE IF NOT EXISTS MRIDataSet (
                                    directory text NOT NULL,
                                    img_quality_score float NOT NULL,
                                    img_slice_score float NOT NULL,
                                    weighted_score float NOT NULL,
                                    total_slice int NOT NULL,
                                    time_consuming text NOT NULL
                                );"""

    # create tables
    if conn is not None:
        # create MRI table
        c = conn.cursor()
        c.execute(sql_create_mri_table)
    else:
        print("Error! cannot create the databse connection")

def close_databse(conn):
    """
    Close current database
    :param conn
    :return:
    """
    if conn:
        conn.close()

def create_record(conn, record):
    sql = ''' INSERT INTO MRIDataSet(directory, img_quality_score, img_slice_score, weighted_score, total_slice, time_consuming)
                VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, record)
    # save changes
    conn.commit()
    return cur.lastrowid

def delete_record(conn, id):
    """
    Delete record with id
    :param conn:
    :param id: record id
    :return:
    """
    sql = 'DELETE FROM MRIDataSet WHERE ROWID=?'
    cur = conn.cursor()
    cur.execute(sql, (id, ))
    conn.commit()

def query_task(conn, desc, des):
    cur = conn.cursor()
    sql = ""
    if des == 'True':
        sql = 'SELECT * FROM MRIDataSet ORDER BY ' + desc + ' DESC;'
    else:
        sql = 'SELECT * FROM MRIDataSet ORDER BY ' + desc + ' ASC;'
    global row
    cur.execute(sql)

    table = from_db_cursor(cur)
    
    print(table)

def check_record(conn, directory):
    sql = f'SELECT EXISTS(SELECT 1 FROM MRIDataSet WHERE directory = "{directory}")'
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchone()[0]
    return result
    

def main(root, hdr):
    '''
    :param root: top level root directory containing mri in different date
    :return:
    '''
    for subdir in os.listdir(root):

        subroot = root + subdir

        print(f"Processing directory {subroot}")
        database = subroot + "/" + subdir + ".db"
        if os.path.exists(database):
            print(f"{database} has been created before!")
            continue
        conn = create_connection(database)
        create_table(conn)

        t = Timer()

        # has to use with first
        # otherwise the record cannot be recorded
        # root = "../data/MRI Data/ENT0004/20190925/"

        # no subsubdir
        if not os.path.isdir(subroot+ "/" + os.listdir(subroot)[1]):
            with conn:
            # delete_record(conn, 1)
            # process current directory
                try:
                    # timer start to count
                    t.start()
                    img_score, slice_score, num_slice, weighted_score = directory_score(subroot + "/", hdr)
                    elapsed_time = t.stop()
                    # when img is too bad there is no score
                    if math.isnan(img_score):
                        img_score = weighted_score = 0
                    print(f"{img_score}, {slice_score}, {num_slice}, {weighted_score}")
                    # save record to database
                    record = (dire, img_score, slice_score, weighted_score, num_slice, str(elapsed_time))
                    create_record(conn, record)
                except:
                    pass
        
        else:
            # has subsubdir
            for dire in os.listdir(subroot):
                dir = subroot + "/" + dire + "/"
                # directory check
                if not os.path.isdir(dir):
                    continue
                # record exists
                if check_record(conn, dir) == 1:
                    print(f"record {dir} has been stored!")
                    continue

                with conn:
                # delete_record(conn, 1)
                # process current directory
                    try:
                        # timer start to count
                        t.start()
                        img_score, slice_score, num_slice, weighted_score = directory_score(dir, hdr)
                        elapsed_time = t.stop()
                        # when img is too bad there is no score
                        if math.isnan(img_score):
                            img_score = weighted_score = 0
                        print(f"{img_score}, {slice_score}, {num_slice}, {weighted_score}")
                        # save record to database
                        record = (dire, img_score, slice_score, weighted_score, num_slice, str(elapsed_time))
                        create_record(conn, record)
                    except:
                        pass

        close_databse(conn)

def query_database(query_desc, des):
    database = r"database/mriqc.db"
    conn = create_connection(database)

    query_task(conn, query_desc, des)

    close_databse(conn)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    # parser.add_argument("-q", "--query")
    # parser.add_argument("-d", "--des")


    # if args.query is None or args.des is None:
    #     print("Please specify the query desciption and descending or not")
    #     exit(1)
    parser.add_argument("-r", "--root")
    # 1: enable hdr
    # 0: disable hdr
    parser.add_argument("-f", "--hdr", type=int)
    args = parser.parse_args()
    if args.root is None:
        print("Please specify the root directory of MRI and try again.")
        exit(-1)
    
    # default no hdr
    HDR = False
    if args.hdr == 1:
        HDR = True
    print(HDR)
    main(args.root, HDR)
    # query_database(args.query, args.des)
 