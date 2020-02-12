import sqlite3
from sqlite3 import Error
from mriqa import directory_score
from timer import Timer
from prettytable import PrettyTable, from_db_cursor
import argparse
 
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
    # rows = cur.fetchall()

    # table_row = [desc]
    # table_row += [d for d in row if d not in table_row]
    # table = PrettyTable(row)
    # table.align[desc] = "l" # Left align city names
    # table.padding_width = 1 # One space between column edges and contents (default)

    # for row in rows:

    #     table.add_row(list(row))
    #     # print(row)

    table = from_db_cursor(cur)
    
    print(table)



def main():
    database = r"database/mriqc.db"
    conn = create_connection(database)
    t = Timer()

    # has to use with first
    # otherwise the record cannot be recorded
    with conn:
        # delete_record(conn, 1)
        # process current directory
        t.start()
        dir = "../data/series_216_SGE_fs_ax_113_2.55_256x256/"
        img_score, slice_score, num_slice, weighted_score = directory_score(dir)
        elapsed_time = t.stop()

        record = (dir, img_score, slice_score, weighted_score, num_slice, str(elapsed_time))

        create_record(conn, record)



    close_databse(conn)

def query_database(query_desc, des):
    database = r"database/mriqc.db"
    conn = create_connection(database)

    query_task(conn, query_desc, des)

    close_databse(conn)


if __name__ == "__main__":
    # main()
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query")
    parser.add_argument("-d", "--des")
    args = parser.parse_args()

    if args.query is None or args.des is None:
        print("Please specify the query desciption and descending or not")
        exit(1)

    query_database(args.query, args.des)
