#!/usr/bin/env python3
"""
Update West Lindsey consultations table to include original date columns
and populate them with data from the CSV file
"""
import csv
from backend.database import db

def add_date_columns():
    """Add original date columns to the table"""
    print("Adding original date columns...")

    # Add columns for original dates
    add_columns_sql = """
    ALTER TABLE west_lindsey_consultations
    ADD COLUMN IF NOT EXISTS original_created_time TIMESTAMP,
    ADD COLUMN IF NOT EXISTS original_last_modified_time TIMESTAMP,
    ADD COLUMN IF NOT EXISTS consultation_id INTEGER,
    ADD COLUMN IF NOT EXISTS application_id INTEGER,
    ADD COLUMN IF NOT EXISTS response_published INTEGER,
    ADD COLUMN IF NOT EXISTS consultee_name TEXT,
    ADD COLUMN IF NOT EXISTS consultee_email TEXT,
    ADD COLUMN IF NOT EXISTS consultee_address TEXT;
    """

    success = db.execute_raw(add_columns_sql)
    if success:
        print("✓ Columns added successfully")
    else:
        print("✗ Failed to add columns")
    return success

def update_with_csv_data():
    """Update the table with original CSV data"""
    print("Reading CSV data...")

    csv_file = '/Users/user/Desktop/web scraper/west_lindsey_consultations.csv'

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Parse the data
            consultation_id = row.get('id')
            application_id = row.get('applicationId')
            created_time = row.get('createdTime')
            last_modified_time = row.get('lastModifiedTime')
            opinion = row.get('opinion')
            response_published = row.get('responsePublished')
            response_details = row.get('responseDetailsToPublish')
            consultee_name = row.get('consulteeName')
            consultee_email = row.get('consulteeEmail')
            consultee_address = row.get('consulteeAddress')

            # Update existing records based on description match
            update_sql = """
            UPDATE west_lindsey_consultations
            SET
                original_created_time = %s,
                original_last_modified_time = %s,
                consultation_id = %s,
                application_id = %s,
                response_published = %s,
                consultee_name = %s,
                consultee_email = %s,
                consultee_address = %s,
                status = %s
            WHERE description = %s OR title = %s
            """

            try:
                with db.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(update_sql, (
                            created_time, last_modified_time, consultation_id,
                            application_id, response_published, consultee_name,
                            consultee_email, consultee_address, opinion,
                            response_details, consultee_name
                        ))
                        if cursor.rowcount > 0:
                            print(f"✓ Updated record for {consultee_name}")
                        else:
                            # Insert new record if no match found
                            insert_sql = """
                            INSERT INTO west_lindsey_consultations
                            (title, description, status, original_created_time, original_last_modified_time,
                             consultation_id, application_id, response_published, consultee_name,
                             consultee_email, consultee_address)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            cursor.execute(insert_sql, (
                                consultee_name, response_details, opinion, created_time,
                                last_modified_time, consultation_id, application_id,
                                response_published, consultee_name, consultee_email, consultee_address
                            ))
                            print(f"✓ Inserted new record for {consultee_name}")

                        conn.commit()

            except Exception as e:
                print(f"✗ Error processing {consultee_name}: {e}")

if __name__ == "__main__":
    if add_date_columns():
        update_with_csv_data()
        print("✓ Update complete!")
    else:
        print("✗ Failed to add columns, aborting update")