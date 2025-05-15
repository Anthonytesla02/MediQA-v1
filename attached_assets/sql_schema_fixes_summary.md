
# SQL Schema and Script Fixes Summary

This document summarizes all changes made to your SQL database schema and insert script during our conversation.

---

## 1. Reserved Keyword Fixes (Renaming Tables)

Renamed tables to avoid using SQL reserved keywords:

- `user` → `users`
- `case` → `cases`
- `challenge` → `challenges`
- `flashcard` → `flashcards`
- `achievement` → `achievements`

---

## 2. Table Creation Fixes

### General Enhancements:
- Added `IF NOT EXISTS` to all `CREATE TABLE` statements.
- Ensured all foreign key references explicitly point to primary key columns.

### Foreign Key Handling:
- All foreign keys are marked `NOT NULL` unless needed otherwise.
- Added `ON DELETE CASCADE` to clean up dependent records when parent rows are deleted.

---

## 3. Data Type and Structure Cleanup

- Removed unnecessary double quotes around column names (e.g., `"name"` to `name`).
- Standardized all table names to lowercase and plural for consistency.

---

## 4. Fixes to Insert Script

- Updated `INSERT INTO achievement` to `INSERT INTO achievements`.
- Cleaned up column quoting in the insert statement.

### Final Insert Command:
```sql
INSERT INTO achievements (name, description, badge_icon, points)
VALUES
    ('First Login', 'Logged in for the first time', 'award', 5),
    ('Streak Starter', 'Maintained a 3-day streak', 'calendar', 10),
    ('Consistent Learner', 'Maintained a 7-day streak', 'calendar-check', 25),
    ('Diagnosis Expert', 'Correctly diagnosed 5 cases', 'clipboard-check', 25),
    ('Knowledge Seeker', 'Reviewed 10 flashcards', 'book-open', 15),
    ('Quiz Master', 'Completed 3 daily challenges', 'clipboard-pulse', 20);
```

---

## 5. Table Dependency and Creation Order

Verified proper order of table creation:
- `users` must be created before any referencing tables.
- Similarly, `cases`, `challenges`, `flashcards`, and `achievements` are defined before references.

---

## 6. Final Table Names

| Table Name            | Status/Notes                |
|----------------------|-----------------------------|
| `users`              | Renamed from `user`         |
| `chat_history`       | OK as-is                    |
| `cases`              | Renamed from `case`         |
| `case_attempt`       | OK as-is                    |
| `challenges`         | Renamed from `challenge`    |
| `challenge_attempt`  | OK as-is                    |
| `flashcards`         | Renamed from `flashcard`    |
| `flashcard_progress` | OK as-is                    |
| `achievements`       | Renamed from `achievement`  |
| `user_achievement`   | OK as-is                    |

---

Let us know if you need this exported to `.sql` as well, or if you'd like seed data for other tables.
