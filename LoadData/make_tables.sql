create table if not exists syn(category varchar(30), canon varchar(30), syn varchar(100), primarykey varchar(50));
create table if not exists courses(course_num varchar(5), title varchar(100), units varchar(5), area varchar(10), term varchar(10), pre varchar(200), description varchar(700));
create table if not exists polyratings(primarykey varchar(50), dept varchar(6), evals varchar(5), first varchar(20), last varchar(20), rating varchar(6), lettergrade varchar(1), numgrade varchar(6), avgyear varchar(6), college varchar(6));
create table if not exists faculty(name varchar(35), username varchar(20), title varchar(20), phone varchar(14), office varchar(20), hours varchar(60));
create table if not exists sections(course_name varchar(120), section varchar(6), types varchar(20), days varchar(100), starttime varchar(20), endtime varchar(20), location varchar(60), roomnumber varchar(13));
