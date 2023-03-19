
----procesamientos---


---crear tabla con usuarios con más de 100 películas calificadas y menos de 1000

drop table if exists ratings_sel;

create table ratings_sel as 

select userId, count(*) as cnt_rat
from ratings
group by userId
having cnt_rat >=100 and cnt_rat <= 1000
order by cnt_rat desc ;



---crear tabla con películas que han sido calificadas por más de 50 usuarios
drop table if exists peliculas_sel;



create table movies_sel as select movieId,
                         count(*) as cnt_rat
                         from ratings
                         group by movieId
                         having cnt_rat >=50
                         order by cnt_rat desc ;


-------crear tablas filtradas de libros, usuarios y calificaciones ----

drop table if exists ratings_final;

create table ratings_final as
select a.userId,
a.movieId ,
a.rating 
from ratings a 
inner join movies_sel b
on a.movieId =b.movieId
inner join ratings_sel c
on a.userId =c.userId;


drop table if exists movies_final;

create table movies_final as
select a.movieId,
a.title,
a.year,
a.Action,
a.Adventure,
a.Animation,
a.Children,
a.Comedy,
a.Crime,
a.Documentary,
a.Drama,
a.Fantasy,
a."Film-Noir" as Film_Noir,
a.Horror,
a.IMAX,
a.Musical,
a.Mystery,
a.Romance,
a."Sci-Fi" as Sci_Fi,
a.Thriller,
a.War,
a.Western,
a."(no genres listed)" as no_genres_listed,
from movies a
inner join movies_sel c
on a.movieId= c.movieId;

---crear tabla completa ----

drop table if exists full_ratings ;

create table full_ratings as select 
a.rating ,
b.*,
 from ratings_final a inner join
 movies_final b on a.userId=b.userId;



