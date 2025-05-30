-- Datadog user
CREATE LOGIN datadog WITH PASSWORD = 'Password12!';
CREATE USER datadog FOR LOGIN datadog;
GRANT SELECT on sys.dm_os_performance_counters to datadog;
GRANT VIEW SERVER STATE to datadog;
GRANT CONNECT ANY DATABASE to datadog;
GRANT VIEW ANY DEFINITION to datadog;

-- Test users
CREATE LOGIN bob WITH PASSWORD = 'Password12!';
CREATE USER bob FOR LOGIN bob;
GRANT CONNECT ANY DATABASE to bob;
CREATE LOGIN fred WITH PASSWORD = 'Password12!';
CREATE USER fred FOR LOGIN fred;
GRANT CONNECT ANY DATABASE to fred;
GO

-- Create test procedure for metrics loading feature.
USE master;
GO
CREATE PROCEDURE pyStoredProc
    AS BEGIN
        CREATE TABLE #Datadog
        (
            [metric] varchar(255) NOT NULL,
            [type] varchar(50) NOT NULL,
            [value] float NOT NULL,
            [tags] varchar(255)
        )
        SET NOCOUNT ON;
        INSERT INTO #Datadog (metric, type, value, tags) VALUES
            ('sql.sp.testa', 'gauge', 100, 'foo:bar,baz:qux'),
            ('sql.sp.testb', 'gauge', 1, 'foo:bar,baz:qux'),
            ('sql.sp.testb', 'gauge', 2, 'foo:bar,baz:qux');
        SELECT * FROM #Datadog;
    END;
GO
GRANT EXECUTE on pyStoredProc to datadog;
GO

CREATE PROCEDURE exampleProcWithoutNocount AS
BEGIN
    CREATE TABLE #Hello
    (
        [value] int not null,
    )
    INSERT INTO #Hello VALUES (1)
    select * from #Hello;
END;
GO
GRANT EXECUTE on exampleProcWithoutNocount to datadog;
GO

CREATE PROCEDURE encryptedProc WITH ENCRYPTION AS
BEGIN
    select count(*) from sys.databases;
END;
GO
GRANT EXECUTE on encryptedProc to bob;
GO

-- create test procedure with multiple queries
CREATE PROCEDURE multiQueryProc AS
BEGIN
    declare @total int = 0;
    select @total = @total + count(*) from sys.databases where name like '%_';
    select @total = @total + count(*) from sys.sysobjects where type = 'U';
    select @total;
END;
GO
GRANT EXECUTE on multiQueryProc to bob;
GO

-- test procedure with IF ELSE branches and temp tables
CREATE PROCEDURE conditionalPlanTest
 @Switch INTEGER
AS
BEGIN
 SET NOCOUNT ON
 CREATE TABLE #Ids (Id INTEGER PRIMARY KEY)

 IF (@Switch > 0)
  BEGIN
   INSERT INTO #Ids (Id) VALUES (1)
  END 

 IF (@Switch > 1)
  BEGIN
   INSERT #Ids (Id) VALUES (2)
  END

 SELECT * FROM #Ids
END
GO
GRANT EXECUTE on conditionalPlanTest to bob;
GO

CREATE PROCEDURE procedureWithLargeCommment AS
/* 
author: Datadog 
usage: some random comments
test: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
description: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
this comment has no actual meanings, just to test large sp with truncation
the quick brown fox jumps over the lazy dog, the quick brown fox jumps over the lazy dog, the quick brown fox jumps over the lazy dog
*/
BEGIN
    SELECT * FROM ϑings;
END;
GO
GRANT EXECUTE on procedureWithLargeCommment to bob;
GRANT EXECUTE on procedureWithLargeCommment to fred;
GO

-- test procedure with embedded null characters
CREATE PROCEDURE nullCharTest
AS
BEGIN
 SELECT * FROM ϑings WHERE name = 'foo\x00';
END;
GO
GRANT EXECUTE on nullCharTest to bob;
GRANT EXECUTE on nullCharTest to fred;
GO

-- Create test database for integration schema tests
CREATE DATABASE datadog_test_schemas;
GO
USE datadog_test_schemas;
GO

CREATE SCHEMA test_schema;
GO

-- Create the partition function
CREATE PARTITION FUNCTION CityPartitionFunction (INT)
AS RANGE LEFT FOR VALUES (100, 200, 300); -- Define your partition boundaries here

-- Create the partition scheme
CREATE PARTITION SCHEME CityPartitionScheme
AS PARTITION CityPartitionFunction ALL TO ([PRIMARY]); -- Assign partitions to filegroups

-- Create the partitioned table
CREATE TABLE datadog_test_schemas.test_schema.cities (
    id INT NOT NULL DEFAULT 0,
    name VARCHAR(255),
    population INT NOT NULL DEFAULT 0,
    CONSTRAINT PK_Cities PRIMARY KEY (id)
) ON CityPartitionScheme(id); -- Assign the partition scheme to the table

-- Create indexes
CREATE INDEX two_columns_index ON datadog_test_schemas.test_schema.cities (id, name);
CREATE INDEX single_column_index ON datadog_test_schemas.test_schema.cities (population);

INSERT INTO datadog_test_schemas.test_schema.cities  VALUES (1, 'yey', 100), (2, 'bar', 200);
GO

-- Create table with a foreign key
CREATE TABLE datadog_test_schemas.test_schema.landmarks (name varchar(255), city_id int DEFAULT 0);
GO
ALTER TABLE datadog_test_schemas.test_schema.landmarks ADD CONSTRAINT FK_CityId 
FOREIGN KEY (city_id) REFERENCES datadog_test_schemas.test_schema.cities(id)
ON DELETE SET NULL;
GO

-- Create table with unique constraint
CREATE TABLE datadog_test_schemas.test_schema.Restaurants (
    RestaurantName VARCHAR(255),
    District VARCHAR(100),
    Cuisine VARCHAR(100),
    CONSTRAINT UC_RestaurantNameDistrict UNIQUE (RestaurantName, District)
);
GO

-- Create table with a foreign key on two columns
CREATE TABLE datadog_test_schemas.test_schema.RestaurantReviews (
    RestaurantName VARCHAR(255),
    District VARCHAR(100),
    Review VARCHAR(MAX),
    CONSTRAINT FK_RestaurantNameDistrict FOREIGN KEY (RestaurantName, District)
        REFERENCES datadog_test_schemas.test_schema.Restaurants(RestaurantName, District)
        ON DELETE CASCADE
        ON UPDATE SET NULL
);
GO

-- Create second test database for integration schema tests
CREATE DATABASE datadog_test_schemas_second;
GO
USE datadog_test_schemas_second;
-- This table is pronounced "things" except we've replaced "th" with the greek lower case "theta" to ensure we
-- correctly support unicode throughout the integration.
CREATE TABLE datadog_test_schemas_second.dbo.ϑings (id int DEFAULT 0, name varchar(255));
INSERT INTO datadog_test_schemas_second.dbo.ϑings VALUES (1, 'foo'), (2, 'bar');
CREATE USER bob FOR LOGIN bob;
CREATE USER fred FOR LOGIN fred;
CREATE CLUSTERED INDEX thingsindex ON datadog_test_schemas_second.dbo.ϑings (name);
GO

-- Create an alternate collation database to test handling of case sensitivity
CREATE DATABASE datadog_test_collation
    COLLATE Latin1_General_100_BIN2;
GO

-- Create test database for integration tests.
-- Only bob and fred have read/write access to this database.
CREATE DATABASE [datadog_test-1];
GO
USE [datadog_test-1];
GO

CREATE USER bob FOR LOGIN bob;
GRANT VIEW DEFINITION TO bob;
CREATE USER fred FOR LOGIN fred;
GRANT VIEW DEFINITION TO fred;
GO

EXEC sp_addrolemember 'db_datareader', 'bob'
EXEC sp_addrolemember 'db_datawriter', 'bob'
EXEC sp_addrolemember 'db_datareader', 'fred'
GO

CREATE PROCEDURE bobProc AS
BEGIN
    SELECT * FROM ϑings;
END;
GO

CREATE PROCEDURE bobProcParams @P1 INT = NULL, @P2 nvarchar(8) = NULL AS
BEGIN
    SELECT * FROM ϑings WHERE id = @P1;
    SELECT id FROM ϑings WHERE name = @P2;
END;
GO

CREATE PROCEDURE fredProcParams @Name nvarchar(8) = NULL AS
BEGIN
    SELECT * FROM ϑings WHERE name like @Name;
END;
GO

GRANT EXECUTE on bobProcParams to bob;
GRANT EXECUTE on bobProc to bob;
GRANT EXECUTE on fredProcParams to fred;
GRANT EXECUTE on bobProc to fred;
GO

-- create an offline database to have an unavailable database to test with
CREATE DATABASE unavailable_db;
GO
ALTER DATABASE unavailable_db SET OFFLINE;
GO

-- create a a restricted database to ensure the agent gracefully handles not being able to connect
-- to it
CREATE DATABASE restricted_db;
GO
ALTER DATABASE restricted_db SET RESTRICTED_USER
GO

-- This table is pronounced "things" except we've replaced "th" with the greek lower case "theta" to ensure we
-- correctly support unicode throughout the integration.
CREATE TABLE [datadog_test-1].dbo.ϑings (id int, name varchar(255));
INSERT INTO [datadog_test-1].dbo.ϑings VALUES (1, 'foo'), (2, 'bar');
CREATE CLUSTERED INDEX thingsindex ON [datadog_test-1].dbo.ϑings (name);

-- Table variables
DECLARE @table_prefix VARCHAR(100) = 'CREATE TABLE [datadog_test-1].dbo.'
DECLARE @table_columns VARCHAR(500) = ' (id INT NOT NULL IDENTITY, col1_txt TEXT, col2_txt TEXT, col3_txt TEXT, col4_txt TEXT, col5_txt TEXT, col6_txt TEXT, col7_txt TEXT, col8_txt TEXT, col9_txt TEXT, col10_txt TEXT, col11_float FLOAT, col12_float FLOAT, col13_float FLOAT, col14_int INT, col15_int INT, col16_int INT, col17_date DATE, PRIMARY KEY(id));';

-- Create a simple table for deadlocks
CREATE TABLE [datadog_test-1].dbo.deadlocks (a int PRIMARY KEY not null ,b int null); 

INSERT INTO [datadog_test-1].dbo.deadlocks VALUES (1,10),(2,20),(3,30) 

-- Grant permissions to bob and fred to update the deadlocks table
GRANT INSERT ON [datadog_test-1].dbo.deadlocks TO bob;
GRANT UPDATE ON [datadog_test-1].dbo.deadlocks TO bob;
GRANT DELETE ON [datadog_test-1].dbo.deadlocks TO bob;

GRANT INSERT ON [datadog_test-1].dbo.deadlocks TO fred;
GRANT UPDATE ON [datadog_test-1].dbo.deadlocks TO fred;
GRANT DELETE ON [datadog_test-1].dbo.deadlocks TO fred;
GO

-- Create a main table which contains high cardinality data for testing.
DECLARE @main_table_query VARCHAR(600) = @table_prefix + 'high_cardinality' + @table_columns;
EXEC (@main_table_query);

-- Insert random data into the main table.
-- Loop variables
DECLARE @row_count INT = 1;
DECLARE @rows_to_insert INT = 100;
WHILE @row_count <= @rows_to_insert
BEGIN
    DECLARE @col1_txt VARCHAR(225) = CONVERT(varchar(225), NEWID());
    DECLARE @col2_txt VARCHAR(225) = CONVERT(varchar(225), NEWID());
    DECLARE @col3_txt VARCHAR(225) = CONVERT(varchar(225), NEWID());
    DECLARE @col4_txt VARCHAR(225) = CONVERT(varchar(225), NEWID());
    DECLARE @col5_txt VARCHAR(225) = CONVERT(varchar(225), NEWID());
    DECLARE @col6_txt VARCHAR(225) = CONVERT(varchar(225), NEWID());
    DECLARE @col7_txt VARCHAR(225) = CONVERT(varchar(225), NEWID());
    DECLARE @col8_txt VARCHAR(225) = CONVERT(varchar(225), NEWID());
    DECLARE @col9_txt VARCHAR(225) = CONVERT(varchar(225), NEWID());
    DECLARE @col10_txt VARCHAR(225) = CONVERT(varchar(225), NEWID());
    DECLARE @col11_float FLOAT = RAND() * 200;
    DECLARE @col12_float FLOAT = RAND() * 800;
    DECLARE @col13_float FLOAT = RAND() * 350;
    DECLARE @col14_int INT = FLOOR(RAND() * 800);
    DECLARE @col15_int INT = FLOOR(RAND() * 1500);
    DECLARE @col16_int INT = FLOOR(RAND() * 2500);
    DECLARE @col17_date DATE = CAST(CAST(RAND()*100000 AS INT) AS DATETIME);

    INSERT INTO [datadog_test-1].dbo.high_cardinality (col1_txt, col2_txt, col3_txt, col4_txt, col5_txt, col6_txt, col7_txt, col8_txt, col9_txt, col10_txt, col11_float, col12_float, col13_float, col14_int, col15_int, col16_int, col17_date) VALUES (@col1_txt, @col2_txt, @col3_txt, @col4_txt, @col5_txt, @col6_txt, @col7_txt, @col8_txt, @col9_txt, @col10_txt, @col11_float, @col12_float, @col13_float, @col14_int, @col15_int, @col16_int, @col17_date);

    SET @row_count = @row_count + 1
END;

-- Load the database with many users, schemas, and tables.
-- User variables
DECLARE @user VARCHAR(50);
DECLARE @user_login_query VARCHAR(200);
DECLARE @user_create_query VARCHAR(200);
-- Schema variables
DECLARE @schema_name VARCHAR(50);
DECLARE @schema_query VARCHAR(200);
-- Table variables
DECLARE @table_name VARCHAR(100);
DECLARE @table_query VARCHAR(600);
-- Loop variables
DECLARE @object_count INT = 1;
DECLARE @objects_to_create INT = 2000;
WHILE @object_count <= @objects_to_create
BEGIN
    SET @user = 'high_cardinality_user_' + CAST(@object_count AS VARCHAR);
    SET @user_login_query = 'CREATE LOGIN ' + @user + ' WITH PASSWORD = ''Password12!'';';
    SET @user_create_query = 'CREATE USER ' + @user + ' FOR LOGIN ' + @user + ';';
    EXEC (@user_login_query);
    EXEC (@user_create_query);

    SET @schema_name = 'high_cardinality_schema_' + CAST(@object_count AS VARCHAR);
    SET @schema_query = 'CREATE SCHEMA ' + @schema_name;
    EXEC (@schema_query);

    SET @table_name = 'high_cardinality_' + CAST(@object_count AS VARCHAR);
    SET @table_query = @table_prefix + @table_name + @table_columns;
    EXEC (@table_query);

    SET @object_count = @object_count + 1;
END;

CREATE EVENT SESSION datadog
ON SERVER
ADD EVENT sqlserver.xml_deadlock_report 
ADD TARGET package0.ring_buffer 
WITH (
    MAX_MEMORY = 1024 KB, 
    EVENT_RETENTION_MODE = ALLOW_SINGLE_EVENT_LOSS, 
    MAX_DISPATCH_LATENCY = 120 SECONDS, 
    STARTUP_STATE = ON 
);
GO

ALTER EVENT SESSION datadog ON SERVER STATE = START;
GO

-- 1. Query completions (grouped)
-- Includes RPC completions, batch completions, and stored procedure completions
IF EXISTS (
    SELECT * FROM sys.server_event_sessions WHERE name = 'datadog_query_completions'
)
    DROP EVENT SESSION datadog_query_completions ON SERVER;
GO

CREATE EVENT SESSION datadog_query_completions ON SERVER
ADD EVENT sqlserver.rpc_completed (
    ACTION (
        sqlserver.sql_text,
        sqlserver.database_name,
        sqlserver.username,
        sqlserver.client_app_name,
        sqlserver.client_hostname,
        sqlserver.session_id,
        sqlserver.request_id
    )
    WHERE (
        sql_text <> '' AND
        duration > 1000000 -- in microseconds, 1 second
    )
),
ADD EVENT sqlserver.sql_batch_completed(
    ACTION (
        sqlserver.sql_text,
        sqlserver.database_name,
        sqlserver.username,
        sqlserver.client_app_name,
        sqlserver.client_hostname,
        sqlserver.session_id,
        sqlserver.request_id
    )
    WHERE (
        sql_text <> '' AND
        duration > 1000000
    )
),
ADD EVENT sqlserver.module_end(
    SET collect_statement = (1)
    ACTION (
        sqlserver.sql_text,
        sqlserver.database_name,
        sqlserver.username,
        sqlserver.client_app_name,
        sqlserver.client_hostname,
        sqlserver.session_id,
        sqlserver.request_id
    )
    WHERE (
        sql_text <> '' AND
        duration > 1000000
    )
)
ADD TARGET package0.ring_buffer
WITH (
    MAX_MEMORY = 2048 KB,
    TRACK_CAUSALITY = ON,
    EVENT_RETENTION_MODE = ALLOW_SINGLE_EVENT_LOSS,
    MAX_DISPATCH_LATENCY = 3 SECONDS,
    STARTUP_STATE = ON
);
GO

-- 2. Errors and Attentions (grouped)
IF EXISTS (
    SELECT * FROM sys.server_event_sessions WHERE name = 'datadog_query_errors'
)
    DROP EVENT SESSION datadog_query_errors ON SERVER;
GO
CREATE EVENT SESSION datadog_query_errors ON SERVER
-- Low-frequency events: send to ring_buffer
ADD EVENT sqlserver.error_reported(
    ACTION(
        sqlserver.sql_text,
        sqlserver.database_name,
        sqlserver.username,
        sqlserver.client_app_name,
        sqlserver.client_hostname,
        sqlserver.session_id,
        sqlserver.request_id
    )
    WHERE severity >= 11
),
ADD EVENT sqlserver.attention(
    ACTION(
        sqlserver.sql_text,
        sqlserver.database_name,
        sqlserver.username,
        sqlserver.client_app_name,
        sqlserver.client_hostname,
        sqlserver.session_id,
        sqlserver.request_id
    )
)
ADD TARGET package0.ring_buffer
WITH (
    MAX_MEMORY = 2048 KB,
    EVENT_RETENTION_MODE = ALLOW_SINGLE_EVENT_LOSS,
    MAX_DISPATCH_LATENCY = 30 SECONDS,
    STARTUP_STATE = ON
);

ALTER EVENT SESSION datadog_query_completions ON SERVER STATE = START;
ALTER EVENT SESSION datadog_query_errors ON SERVER STATE = START;