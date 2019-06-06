use jpatel26466;

drop table if exists questions;
create table questions
(
    qid       int primary key not null auto_increment,
    theme    varchar(30),
    question varchar(300),
    answerId int
);

load data local infile 'questions.tsv'
    into table questions
    fields terminated by '\t' enclosed by ''
    lines terminated by '\n' starting by ''
    ignore 1 lines
    (theme, question, answerId, @dummy, @dummy);
