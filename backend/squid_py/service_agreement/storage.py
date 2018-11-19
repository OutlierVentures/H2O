import sqlite3


def record_service_agreement(storage_path, service_agreement_id, did, status='pending'):
    """ Records the given pending service agreement.
    """
    conn = sqlite3.connect(storage_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS service_agreements
               (id VARCHAR PRIMARY KEY, did VARCHAR, status VARCHAR(10));'''
        )
        cursor.execute(
            'INSERT OR REPLACE INTO service_agreements VALUES (?,?,?)',
            [service_agreement_id, did, status],
        )
        conn.commit()
    finally:
        conn.close()


def get_service_agreements(storage_path, status='pending'):
    conn = sqlite3.connect(storage_path)
    try:
        cursor = conn.cursor()
        return [row for row in
                cursor.execute("SELECT * FROM service_agreements WHERE status='%s';" % status)]
    finally:
        conn.close()


