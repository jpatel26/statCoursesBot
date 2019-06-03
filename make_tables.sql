create table if not exists syn(category varchar(30), canon varchar(30), syn varchar(100), primarykey varchar(50));
create table if not exists courses(course_num varchar(5), title varchar(100), units varchar(5), area varchar(10), term varchar(10), pre varchar(200), description varchar(700));
create table if not exists polyratings(primarykey varchar(50), dept varchar(6), evals varchar(5), first varchar(20), last varchar(20), rating varchar(6), lettergrade varchar(1), numgrade varchar(6), avgyear varchar(6), college varchar(6));
