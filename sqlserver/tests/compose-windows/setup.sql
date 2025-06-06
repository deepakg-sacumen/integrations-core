------------------------------ COMMON SETUP ------------------------------
ALTER login sa ENABLE;
GO
ALTER login sa WITH PASSWORD = 'Password123';
GO

-- datadog user
CREATE LOGIN datadog WITH PASSWORD = 'Password12!';
CREATE USER datadog FOR LOGIN datadog;
GRANT SELECT on sys.dm_os_performance_counters to datadog;
GRANT VIEW SERVER STATE to datadog;
GRANT VIEW ANY DEFINITION to datadog;


-- test users
CREATE LOGIN bob WITH PASSWORD = 'Password12!';
CREATE USER bob FOR LOGIN bob;
CREATE LOGIN fred WITH PASSWORD = 'Password12!';
CREATE USER fred FOR LOGIN fred;
GO

-- note that we deliberately don't grant "CONNECT ANY DATABASE" to the agent user here because that
-- permission is not supported in SQL Server 2012. This is OK for the integration tests because in
-- the tests instead we explicitly create the datadog user in each database as a workaround
USE model;
GO
CREATE USER datadog FOR LOGIN datadog;
GO
USE msdb;
GO
CREATE USER datadog FOR LOGIN datadog;
GRANT SELECT to datadog;
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
ALTER TABLE datadog_test_schemas.test_schema.landmarks ADD CONSTRAINT FK_CityId FOREIGN KEY (city_id)
REFERENCES datadog_test_schemas.test_schema.cities(id)
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
USE datadog_test_collation;
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
CREATE TABLE datadog_test_collation.test_schema.cities (
    id INT NOT NULL DEFAULT 0,
    name VARCHAR(255),
    population INT NOT NULL DEFAULT 0,
    CONSTRAINT PK_Cities PRIMARY KEY (id)
) ON CityPartitionScheme(id); -- Assign the partition scheme to the table

-- Create indexes
CREATE INDEX two_columns_index ON datadog_test_collation.test_schema.cities (id, name);
CREATE INDEX single_column_index ON datadog_test_collation.test_schema.cities (population);

INSERT INTO datadog_test_collation.test_schema.cities  VALUES (1, 'yey', 100), (2, 'bar', 200);
GO

-- Create table with a foreign key
CREATE TABLE datadog_test_collation.test_schema.landmarks (name varchar(255), city_id int DEFAULT 0);
GO
ALTER TABLE datadog_test_collation.test_schema.landmarks ADD CONSTRAINT FK_CityId FOREIGN KEY (city_id)
REFERENCES datadog_test_collation.test_schema.cities(id)
ON DELETE SET NULL;
GO

-- Create table with unique constraint
CREATE TABLE datadog_test_collation.test_schema.Restaurants (
    RestaurantName VARCHAR(255),
    District VARCHAR(100),
    Cuisine VARCHAR(100),
    CONSTRAINT UC_RestaurantNameDistrict UNIQUE (RestaurantName, District)
);
GO

-- Create table with a foreign key on two columns
CREATE TABLE datadog_test_collation.test_schema.RestaurantReviews (
    RestaurantName VARCHAR(255),
    District VARCHAR(100),
    Review VARCHAR(MAX),
    CONSTRAINT FK_RestaurantNameDistrict FOREIGN KEY (RestaurantName, District)
        REFERENCES datadog_test_collation.test_schema.Restaurants(RestaurantName, District)
        ON DELETE CASCADE
        ON UPDATE SET NULL
);
GO


-- Create test database for integration tests
-- only bob and fred have read/write access to this database
-- the datadog user has only connect access but can't read any objects
CREATE DATABASE [datadog_test-1];
GO
USE [datadog_test-1];
GO

-- This table is pronounced "things" except we've replaced "th" with the greek lower case "theta" to ensure we
-- correctly support unicode throughout the integration.
CREATE TABLE [datadog_test-1].dbo.ϑings (id int, name varchar(255));
INSERT INTO [datadog_test-1].dbo.ϑings VALUES (1, 'foo'), (2, 'bar');
CREATE CLUSTERED INDEX thingsindex ON [datadog_test-1].dbo.ϑings (name);
CREATE USER bob FOR LOGIN bob;
CREATE USER fred FOR LOGIN fred;
-- we don't need to recreate the datadog user in this new DB because it already exists in the model
-- database so it's copied by default to new databases
GO

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

EXEC sp_addrolemember 'db_datareader', 'bob'
EXEC sp_addrolemember 'db_datareader', 'fred'
EXEC sp_addrolemember 'db_datawriter', 'bob'
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

-- create test procedure for metrics loading feature
USE master;
GO
CREATE PROCEDURE pyStoredProc AS
BEGIN
    CREATE TABLE #Datadog
    (
        [metric] varchar(255) not null,
        [type] varchar(50) not null,
        [value] float not null,
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