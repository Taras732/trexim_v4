-- PostgreSQL setup script for Trexim
-- Run this after starting PostgreSQL service

-- Create database (run as postgres superuser)
CREATE DATABASE trexim;

-- Create user
CREATE USER trexim WITH PASSWORD 'trexim2026';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE trexim TO trexim;

-- Connect to trexim database and grant schema privileges
\c trexim
GRANT ALL ON SCHEMA public TO trexim;
