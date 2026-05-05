USE hospital_management;

-- ─────────────────────────────────────────────
--  USER-DEFINED FUNCTIONS (UDFs)
-- ─────────────────────────────────────────────

DELIMITER $$

-- ── fn_cal_age ───────────────────────────────────────────────────────────────
-- Calculate a patient's current age in full years from their date of birth.
-- Used in patient reports and age-group classification queries.

DROP FUNCTION IF EXISTS fn_cal_age $$
CREATE FUNCTION fn_cal_age (p_DateOfBirth DATE)
RETURNS INT
DETERMINISTIC
BEGIN
    RETURN TIMESTAMPDIFF(YEAR, p_DateOfBirth, CURDATE());
END $$


-- ── fn_gen_id ────────────────────────────────────────────────────────────────
-- Auto-generate the next sequential PatientID in the format P0001, P0002, …
-- Called from Python's patient_add() before INSERT.

DROP FUNCTION IF EXISTS fn_gen_id;

CREATE FUNCTION fn_gen_id ()
RETURNS VARCHAR(20)
READS SQL DATA
BEGIN
    DECLARE max_num   INT;
    DECLARE new_pat_id VARCHAR(20);

    -- Lấy từ ký tự thứ 4 trở đi (bỏ qua 'PAT') để tìm số lớn nhất
    SELECT MAX(CAST(SUBSTRING(PatientID, 4) AS UNSIGNED))
    INTO max_num
    FROM Patients;

    IF max_num IS NULL THEN
        SET max_num = 1;
    ELSE
        SET max_num = max_num + 1;
    END IF;

    -- Nối chữ 'PAT' với bộ đếm, tự động điền số 0 cho đủ 3 chữ số
    SET new_pat_id = CONCAT('PAT', LPAD(max_num, 3, '0'));
    RETURN new_pat_id;
END $$



-- ── fn_dept_fee ──────────────────────────────────────────────────────────────
-- Apply a department-specific billing surcharge.
-- Departments DE004 and DE006 carry a 20% surcharge (e.g. ICU, surgery).
-- Returns the adjusted amount rounded to 2 decimal places.

DROP FUNCTION IF EXISTS fn_dept_fee $$
CREATE FUNCTION fn_dept_fee (
    p_BaseAmount   DECIMAL(15, 2),
    p_DepartmentID VARCHAR(20)
)
RETURNS DECIMAL(15, 2)
DETERMINISTIC
BEGIN
    DECLARE multiplier DECIMAL(5, 2) DEFAULT 1.00;

    IF p_DepartmentID IN ('DE004', 'DE006') THEN
        SET multiplier = 1.20;
    END IF;

    RETURN ROUND(p_BaseAmount * multiplier, 2);
END $$

DELIMITER ;
