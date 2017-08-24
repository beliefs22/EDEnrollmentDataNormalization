import sqlite3
import csv
import os


def create_tables(conn):
    """Create SQL tables From text files

    Args:
       conn (:obj: `database connection`): connection to the database to
           save the tables
    """
    # Cursor object
    cur = conn.cursor()
    # get the text files in the CEIRS folder
    os.chdir("..")
    current_files = os.listdir(os.getcwd())
    current_files = [filename
                     for filename in current_files
                     if filename.endswith('.txt')
                     ]
    for filename in current_files:
        with open(filename, 'r') as text_file:
            csvreader = csv.reader(text_file, delimiter='\t')
            table_fields = ",".join(next(csvreader))
            table_data = [row
                          for row in csvreader
                          ]
            # Create Table Statement
            table_title = filename.replace(".txt", "")
            drop_table_sql = """DROP TABLE IF EXISTS {}""".format(table_title)
            create_table_sql = """CREATE TABLE {} ({})""".format(
                table_title, table_fields)
            print("Creating table {}".format(table_title))
            cur.execute(drop_table_sql)
            cur.execute(create_table_sql)

            # Insert Values Statement
            for table_row in table_data:
                transform = "'{}'"
                data_as_text = ",".join([transform.format(item.replace("'", "").replace(",", ""))for item in table_row])
                insert_sql = """INSERT INTO {} VALUES ({})""".format(
                    table_title, data_as_text)
                cur.execute(insert_sql)
            # Commit the changes
            conn.commit()
            print("Done Creating table {}".format(table_title))


def main():
    conn = sqlite3.connect(r'\\win.ad.jhu.edu\cloud\sddesktop$\CEIRS\CEIRS.db')
    create_tables(conn)

if __name__ == "__main__":
    main()
