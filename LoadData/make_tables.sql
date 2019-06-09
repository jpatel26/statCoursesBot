create table if not exists syn
(
    parent_table varchar(30),
    column_name  varchar(30),
    can          varchar(100),
    synon        varchar(600)
);
create table if not exists courses
(
    course_num         varchar(5),
    course_title       varchar(100),
    course_units       varchar(5),
    course_area        varchar(10),
    course_term        varchar(10),
    course_pre         varchar(200),
    course_description varchar(700)
);
create table if not exists polyratings
(
    primarykey           varchar(10),
    dept                 varchar(6),
    num_evals            varchar(5),
    faculty_first_name   varchar(20),
    faculty_last_name    varchar(20),
    faculty_rating       varchar(6),
    faculty_letter_grade varchar(1),
    faculty_num_grade    varchar(6),
    faculty_avgyear      varchar(6),
    college              varchar(6)
);
create table if not exists faculty
(
    faculty_last_name    varchar(30),
    faculty_name         varchar(35),
    faculty_username     varchar(20),
    faculty_title        varchar(20),
    faculty_phone        varchar(14),
    faculty_office       varchar(20),
    faculty_office_hours varchar(60)
);
create table if not exists sections
(
    course_name     varchar(120),
    course_section  varchar(6),
    course_type     varchar(20),
    course_days     varchar(100),
    course_start    varchar(20),
    course_end      varchar(20),
    course_location varchar(60),
    course_room     varchar(13),
    primarykey      varchar(6),
    course_num      varchar(6)
);
create table if not exists faculty_courses
(
    faculty_last_name varchar(30),
    course_num        varchar(60),
    primarykey        varchar(10)
);
create table if not exists data_courses
(
    course_num         varchar(5),
    course_title       varchar(100),
    course_units       varchar(5),
    course_area        varchar(10),
    course_term        varchar(10),
    course_pre         varchar(200),
    course_description varchar(700)
);

create table if not exists course_req
(
   course_num     varchar(6),
   major_req      varchar(2),
   major_elect    varchar(2),
   minor_req      varchar(2)
);

