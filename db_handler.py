import sqlite3

# ==============================
# Database Connection Functions
# ==============================
def get_tables(conn):
    """
    Retrieve all table names from the given database connection.

    Args:
        conn (sqlite3.Connection): The database connection.

    Returns:
        list: A list of table names.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall()]


# ==============================
# Table Data Functions
# ==============================
def fetch_table_data(conn, table):
    """
    Fetch all data from a specified table.

    Args:
        conn (sqlite3.Connection): The database connection.
        table (str): The name of the table.

    Returns:
        list: A list of tuples containing the table data.
    """
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    return cursor.fetchall()


# ==============================
# Table Schema Functions
# ==============================
def fetch_table_schema(conn, table):
    """
    Fetch the schema of a specified table.

    Args:
        conn (sqlite3.Connection): The database connection.
        table (str): The name of the table.

    Returns:
        list: A list of tuples containing the table schema information.
    """
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    return cursor.fetchall()


# ==============================
# Database Comparison Function
# ==============================
def compare_databases(db1_path, db2_path):
    # Create connections to both databases
    conn1 = sqlite3.connect(db1_path)
    conn2 = sqlite3.connect(db2_path)

    # Create cursors for both databases
    cursor1 = conn1.cursor()
    cursor2 = conn2.cursor()

    # Get the list of tables in both databases
    cursor1.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables1 = [row[0] for row in cursor1.fetchall()]

    cursor2.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables2 = [row[0] for row in cursor2.fetchall()]

    # Create dictionaries to store the data for each table
    data1_dict = {}
    data2_dict = {}

    # Iterate over the tables and store the data in dictionaries
    for table in set(tables1) | set(tables2):
        if table in tables1 and table in tables2:
            # Compare the data in the table
            cursor1.execute(f"SELECT * FROM {table}")
            data1 = cursor1.fetchall()

            cursor2.execute(f"SELECT * FROM {table}")
            data2 = cursor2.fetchall()

            if data1 != data2:
                differences.append({
                    'table': table,
                    'data1': data1,
                    'data2': data2
                })
        elif table in tables1:
            only_in_db1.append(table)
        else:
            only_in_db2.append(table)

    # Close the connections
    conn1.close()
    conn2.close()

    return {
        'differences': differences,
        'only_in_db1': only_in_db1,
        'only_in_db2': only_in_db2
    }

