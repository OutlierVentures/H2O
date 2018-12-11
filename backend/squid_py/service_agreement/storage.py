import sqlite3


def record_service_agreement(storage_path, service_agreement_id, did, service_index, price, content_urls, start_time, status='pending'):
    """ Records the given pending service agreement.
    """
    conn = sqlite3.connect(storage_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS service_agreements
               (id VARCHAR PRIMARY KEY, did VARCHAR, service_index INTEGER, 
                price INTEGER, content_urls VARCHAR, start_time INTEGER, status VARCHAR(10));'''
        )
        cursor.execute(
            'INSERT OR REPLACE INTO service_agreements VALUES (?,?,?,?,?,?,?)',
            [service_agreement_id, did, service_index, price, content_urls, start_time, status],
        )
        conn.commit()
    finally:
        conn.close()


def update_service_agreement_status(storage_path, service_agreement_id, status='pending'):
    conn = sqlite3.connect(storage_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE service_agreements SET status=? WHERE id=?',
            (status, service_agreement_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_service_agreements(storage_path, status='pending'):
    conn = sqlite3.connect(storage_path)
    try:
        cursor = conn.cursor()
        return [
            row for row in
            cursor.execute(
                '''
                SELECT id, did, service_index, price, content_urls, start_time, status
                FROM service_agreements 
                WHERE status=?;
                ''',
                (status,))
        ]
    finally:
        conn.close()


