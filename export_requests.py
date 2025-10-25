import sqlite3
import pandas as pd

def export_sqlite_service_requests(db_path='instance/service_portal.db', csv_path='service_requests_export.csv'):
	"""Export service requests to CSV. This function is safe to import and won't run automatically."""
	conn = sqlite3.connect(db_path)
	# Select explicit columns to avoid accidentally exporting other tables or sensitive fields
	query = (
		"SELECT id, service_id, customer_name, customer_email, customer_phone, address, description, urgency, created_at "
		"FROM service_request"
	)
	df = pd.read_sql_query(query, conn)
	print(df)
	df.to_csv(csv_path, index=False)
	print(f"Exported service requests to {csv_path}")
	conn.close()


if __name__ == '__main__':
	export_sqlite_service_requests()
