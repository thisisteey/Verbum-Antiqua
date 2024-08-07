-- Prepares the PostgreSQL server for Verbum Antiqua

-- Drop the database if it already exists
DROP DATABASE IF EXISTS verbum_antiqua_db;

--Create the new database
CREATE DATABASE verbum_antiqua_db
	WITH
	OWNER = postgres
	ENCODING = 'utf8'
	CONNECTION LIMIT = -1;

-- Add a comment on the database
COMMENT ON DATABASE verbum_antiqua_db
	IS 'The database storage for Verbum Antiqua';

-- Drop the role if it already exists
DROP ROLE IF EXISTS verbum_antiqua_user;

-- Create the new role
CREATE ROLE verbum_antiqua_user
	WITH
	LOGIN
	REPLICATION
	BYPASSRLS
	PASSWORD 'verbum_antiqua_pwd';

-- Grant privileges
GRANT ALL ON DATABASE verbum_antiqua_db TO verbum_antiqua_user;
