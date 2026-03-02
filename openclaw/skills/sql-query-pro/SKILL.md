---
name: sql-query-pro
description: Generate, optimize, explain, and debug SQL queries. Supports PostgreSQL, SQLite, MySQL, and SQL Server dialects. Converts natural language to SQL and analyzes query performance.
version: "1.0.0"
source: "online"
tags: [sql, database, query, optimization, utility]
mode: collapse
visibility: shared
permissions:
  agents: [sway, opie, outer]
  execution: "advisory-only"
---

# SQL Query Pro

Generate and optimize SQL queries from natural language descriptions.

## Capabilities

### Query Generation
- Convert natural language to SQL
- Support multiple dialects: PostgreSQL, SQLite, MySQL, SQL Server
- Generate JOINs, subqueries, CTEs, window functions
- Parameterized queries for injection safety

### Query Optimization
- Analyze execution plans (EXPLAIN)
- Suggest index recommendations
- Identify N+1 query patterns
- Recommend query rewrites for performance

### Query Explanation
- Break down complex queries into plain English
- Annotate each clause with its purpose
- Identify potential issues (full table scans, missing indexes)

### Schema Assistance
- Generate CREATE TABLE statements from descriptions
- Suggest normalization improvements
- Design migration scripts

## Output Format

```sql
-- Description: <what the query does>
-- Dialect: PostgreSQL / SQLite / MySQL / SQL Server
-- Performance notes: <optimization suggestions>

SELECT ...
```

## Safety

- Advisory only — does not execute queries
- No database connections
- Always recommends parameterized queries
- Warns about destructive operations (DROP, DELETE, TRUNCATE)
