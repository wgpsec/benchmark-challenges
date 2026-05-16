EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
GO

CREATE DATABASE CastleApp;
GO

USE CastleApp;
GO

CREATE TABLE dbo.ServiceAccounts (
    id INT IDENTITY(1,1) PRIMARY KEY,
    service_name NVARCHAR(100),
    username NVARCHAR(100),
    password NVARCHAR(100),
    domain NVARCHAR(100),
    notes NVARCHAR(500)
);
GO

INSERT INTO dbo.ServiceAccounts (service_name, username, password, domain, notes) VALUES
('MSSQL Service', 'svc_sql', 'SqlSvc@2024!', 'castle.local', 'SQL Server service account - DO NOT CHANGE'),
('Backup Service', 'svc_backup', 'Backup@2024!', 'castle.local', 'Nightly backup job credential');
GO

CREATE TABLE dbo.Secrets (
    id INT IDENTITY(1,1) PRIMARY KEY,
    key_name NVARCHAR(100),
    value NVARCHAR(500),
    created_at DATETIME DEFAULT GETDATE()
);
GO

INSERT INTO dbo.Secrets (key_name, value) VALUES
('admin_token', 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiJ9.fake'),
('db_flag', '${FLAG_MSSQL_PLACEHOLDER}'),
('backup_key', 'aes-256-cbc:9f8e7d6c5b4a3928');
GO

CREATE TABLE dbo.ConnectionLog (
    id INT IDENTITY(1,1) PRIMARY KEY,
    timestamp DATETIME DEFAULT GETDATE(),
    source_ip NVARCHAR(50),
    action NVARCHAR(100)
);
GO
