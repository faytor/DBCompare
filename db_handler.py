import sqlite3

def get_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall()]

def fetch_table_data(conn, table):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    return cursor.fetchall()

def fetch_table_schema(conn, table):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    return cursor.fetchall()

def compare_databases(db1_path, db2_path):
    try:
        conn1 = sqlite3.connect(db1_path)
        conn2 = sqlite3.connect(db2_path)
        
        tables1 = set(get_tables(conn1))
        tables2 = set(get_tables(conn2))
        
        only_in_db1 = tables1 - tables2
        only_in_db2 = tables2 - tables1
        common_tables = tables1.intersection(tables2)
        
        differences = []
        
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
        
        conn1.close()
        conn2.close()
        
        return {
            'only_in_db1': only_in_db1,
            'only_in_db2': only_in_db2,
            'differences': differences
        }
        
    except sqlite3.Error as e:
        return {'error': str(e)}
