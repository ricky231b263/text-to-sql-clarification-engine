CREATE DATABASE IF NOT EXISTS school;
USE school;

DROP TABLE IF EXISTS student;

CREATE TABLE student (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    class VARCHAR(50),
    section VARCHAR(10),
    marks INT
);

INSERT INTO student (name, class, section, marks) VALUES
('Krish', 'Data Science', 'A', 90),
('Sudhanshu', 'Data Science', 'B', 100),
('Darius', 'Data Science', 'A', 86),
('Vikash', 'DEVOPS', 'A', 50),
('Dipesh', 'DEVOPS', 'A', 35);

SELECT * FROM student;