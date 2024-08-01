DATABASE_PATH=/schoolsAPI/db.sqlite3
BUCKET_NAME=cfb-realignment-site
REGION_NAME=us-east-2

aws s3 cp s3://$BUCKET_NAME/database/db.sqlite3 $DATABASE_PATH --region $REGION_NAME
