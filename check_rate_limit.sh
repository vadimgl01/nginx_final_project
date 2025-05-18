typeset -i i=0

while [ $i -lt 40 ]
do
  #curl -s -o /dev/null http://movie_theater.local/users
  #curl -s -o /dev/null -w "%{http_code}\n" http://movie_theater.local/users/
  curl -s  http://movie_theater.local/users/
  let i+=1
done
