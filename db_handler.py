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
    """
    Compare two SQLite databases and return their differences.

    Args:
        db1_path (str): Path to the first database file.
        db2_path (str): Path to the second database file.

    Returns:
        dict: A dictionary containing the comparison results:
            - 'only_in_db1': Set of tables only in the first database.
            - 'only_in_db2': Set of tables only in the second database.
            - 'differences': List of dictionaries containing differences in common tables.
            - 'error': String describing any error that occurred (if applicable).
    """
    try:
        # Connect to databases
        conn1 = sqlite3.connect(db1_path)
        conn2 = sqlite3.connect(db2_path)
        
        # Get table lists
        tables1 = set(get_tables(conn1))
        tables2 = set(get_tables(conn2))
        
        # Compare table lists
        only_in_db1 = tables1 - tables2
        only_in_db2 = tables2 - tables1
        common_tables = tables1.intersection(tables2)
        
        differences = []
        
        # Compare common tables
        for table in common_tables:
            schema1 = fetch_table_schema(conn1, table)
            schema2 = fetch_table_schema(conn2, table)
            
            data1 = fetch_table_data(conn1, table)
            data2 = fetch_table_data(conn2, table)
            
            if schema1 != schema2 or data1 != data2:
                differences.append({
                    'table': table,
                    'schema1': schema1,
                    'schema2': schema2,
                    'data1': data1,
                    'data2': data2
                })
        
        # Close database connections
        conn1.close()
        conn2.close()
        
        return {
            'only_in_db1': only_in_db1,
            'only_in_db2': only_in_db2,
            'differences': differences
        }
        
    except sqlite3.Error as e:
        return {'error': str(e)}
