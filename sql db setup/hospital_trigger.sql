USE hospital_management;

-- ─────────────────────────────────────────────
--  TRIGGERS
-- ─────────────────────────────────────────────

DELIMITER $$

-- ── trg_block_apt_delete ─────────────────────────────────────────────────────
-- Prevent deletion of any appointment that already has one or more linked
-- invoices. Medical records tied to a billing event must be preserved for
-- audit and clinical history purposes.
--
-- NOTE: The Invoices table must have an AppointmentID FK column for this
-- trigger to function. If your schema links invoices to patients only,
-- replace the sub-query with a business-logic check appropriate to your schema.

DROP TRIGGER IF EXISTS trg_block_apt_delete $$
CREATE TRIGGER trg_block_apt_delete
BEFORE DELETE ON Appointments
FOR EACH ROW
BEGIN
    DECLARE inv_count INT DEFAULT 0;

    SELECT COUNT(*) INTO inv_count
    FROM Invoices
    WHERE AppointmentID = OLD.AppointmentID;

    IF inv_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
            'Cannot cancel appointment: one or more invoices are linked to this record.';
    END IF;
END $$


-- ── trg_dept_change_cooldown ──────────────────────────────────────────────────
-- Rate-limit structural changes to the Departments table.
-- A department's name may not be updated more than once within a 30-day window.
-- This guards against accidental or frequent renaming that would create
-- inconsistency in historical records.
--
-- Implementation: uses an audit table dept_change_log to track the most
-- recent update timestamp per department.

DROP TABLE IF EXISTS dept_change_log $$
-- (Re-)create the audit table outside the trigger to avoid DDL inside BEGIN…END
DELIMITER ;

CREATE TABLE IF NOT EXISTS dept_change_log (
    DepartmentID    VARCHAR(20)  NOT NULL PRIMARY KEY,
    LastChangedAt   DATETIME     NOT NULL,
    CONSTRAINT fk_dcl_dept FOREIGN KEY (DepartmentID)
        REFERENCES Departments(DepartmentID) ON DELETE CASCADE
);

DELIMITER $$

DROP TRIGGER IF EXISTS trg_dept_change_cooldown $$
CREATE TRIGGER trg_dept_change_cooldown
BEFORE UPDATE ON Departments
FOR EACH ROW
BEGIN
    DECLARE last_change DATETIME;

    -- Look up the most recent rename for this department
    SELECT LastChangedAt INTO last_change
    FROM dept_change_log
    WHERE DepartmentID = OLD.DepartmentID;

    -- Block the update if it was changed within the last 30 days
    IF last_change IS NOT NULL
       AND TIMESTAMPDIFF(DAY, last_change, NOW()) < 30 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
            'Department name was changed recently. Changes are limited to once every 30 days.';
    END IF;
END $$


-- ── trg_dept_log_after_update ─────────────────────────────────────────────────
-- After a successful department rename, record (or update) the timestamp
-- in dept_change_log so the cooldown trigger has a reference point.

DROP TRIGGER IF EXISTS trg_dept_log_after_update $$
CREATE TRIGGER trg_dept_log_after_update
AFTER UPDATE ON Departments
FOR EACH ROW
BEGIN
    INSERT INTO dept_change_log (DepartmentID, LastChangedAt)
    VALUES (NEW.DepartmentID, NOW())
    ON DUPLICATE KEY UPDATE LastChangedAt = NOW();
END $$


-- ── trg_dept_log_on_insert ────────────────────────────────────────────────────
-- When a new department is added, seed its log entry so the cooldown
-- window starts from the creation date (prevents an immediate rename).

DROP TRIGGER IF EXISTS trg_dept_log_on_insert $$
CREATE TRIGGER trg_dept_log_on_insert
AFTER INSERT ON Departments
FOR EACH ROW
BEGIN
    INSERT INTO dept_change_log (DepartmentID, LastChangedAt)
    VALUES (NEW.DepartmentID, NOW());
END $$

DELIMITER ;
