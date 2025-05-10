-- scripts/database_setup.sql
-- Main database schema for the Nigerian Educational Analytics Project

-- Drop existing database if it exists
DROP DATABASE IF EXISTS edu_analytics;

-- Create database
CREATE DATABASE edu_analytics;
USE edu_analytics;

-- Students table
CREATE TABLE students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    gender VARCHAR(10),
    age INT,
    socioeconomic_status VARCHAR(20),
    parent_education VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Schools table
CREATE TABLE schools (
    school_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    type VARCHAR(20),
    location VARCHAR(20),
    student_count INT,
    teacher_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Teachers table
CREATE TABLE teachers (
    teacher_id INT PRIMARY KEY AUTO_INCREMENT,
    school_id INT,
    subject VARCHAR(50),
    quality_rating INT,
    years_experience INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(school_id)
);

-- Exam results table
CREATE TABLE exam_results (
    result_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    exam_type VARCHAR(20),
    exam_date DATE,
    score INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- Study metrics table
CREATE TABLE study_metrics (
    metric_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    week_starting DATE,
    study_hours INT,
    attendance_rate DECIMAL(5,2),
    extra_tutorials BOOLEAN,
    materials_access BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- Assessments table
CREATE TABLE assessments (
    assessment_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    subject VARCHAR(50),
    assessment_date DATE,
    score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- Interventions table
CREATE TABLE interventions (
    intervention_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    intervention_type VARCHAR(50),
    start_date DATE,
    end_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- Model predictions table
CREATE TABLE predictions (
    prediction_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    predicted_score INT,
    pass_probability DECIMAL(5,2),
    risk_level VARCHAR(20),
    prediction_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- Create view for performance dashboard
CREATE VIEW student_performance_view AS
SELECT 
    s.student_id,
    s.gender,
    s.age,
    s.socioeconomic_status,
    s.parent_education,
    er.exam_type,
    er.score,
    sm.study_hours,
    sm.attendance_rate,
    sm.extra_tutorials,
    sm.materials_access,
    sc.type AS school_type,
    sc.location AS school_location,
    p.predicted_score,
    p.pass_probability,
    p.risk_level
FROM 
    students s
LEFT JOIN
    exam_results er ON s.student_id = er.student_id
LEFT JOIN
    study_metrics sm ON s.student_id = sm.student_id
LEFT JOIN
    schools sc ON s.student_id = sc.school_id
LEFT JOIN
    predictions p ON s.student_id = p.student_id;

-- Create indexes for better performance
CREATE INDEX idx_student_id ON exam_results(student_id);
CREATE INDEX idx_school_id ON teachers(school_id);
CREATE INDEX idx_study_metrics_student ON study_metrics(student_id);
CREATE INDEX idx_assessment_student ON assessments(student_id);

-- Create admin user
CREATE USER IF NOT EXISTS 'edu_admin'@'localhost' IDENTIFIED BY 'edu_analytics_pass';
GRANT ALL PRIVILEGES ON edu_analytics.* TO 'edu_admin'@'localhost';
FLUSH PRIVILEGES;