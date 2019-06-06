use jpatel26466;

-- Some accessor queries to explore the db
-- Real work happens at the bottom
# select f.faculty_last_name
# from faculty f
#          left join
#      polyratings p
#      on f.faculty_last_name = p.faculty_last_name;

# select distinct dept,
#                 num_evals,
#                 faculty_first_name,
#                 faculty_last_name,
#                 faculty_rating,
#                 faculty_letter_grade,
#                 faculty_num_grade,
#                 faculty_avgyear,
#                 college
# from polyratings
# order by faculty_last_name;

# select distinct faculty_last_name,
#                 faculty_name,
#                 faculty_username,
#                 faculty_title,
#                 faculty_phone,
#                 faculty_office,
#                 faculty_office_hours
# from faculty
# order by faculty_last_name;

-- Join the two tables
create table faculty_total
select distinct f.faculty_last_name,
                f.faculty_name,
                f.faculty_username,
                f.faculty_title,
                f.faculty_phone,
                f.faculty_office,
                f.faculty_office_hours,
                p.dept,
                p.num_evals,
                p.faculty_rating,
                p.faculty_letter_grade,
                p.faculty_num_grade,
                p.faculty_avgyear,
                p.college
from faculty f
         left outer join polyratings p
                         on f.faculty_last_name = p.faculty_last_name