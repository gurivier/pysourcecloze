#!/bin/sh

echo '==== ENCLOSE'

python3 pysoclz.py enclose -p samples/C/lexicon.json samples/C/helloworld.c || exit
python3 pysoclz.py enclose -p samples/PHP-HTML/lexicon.json samples/PHP-HTML/power.html || exit
python3 pysoclz.py enclose -p samples/PHP-HTML/lexicon.json samples/PHP-HTML/power.php || exit
python3 pysoclz.py enclose -p samples/SQL/lexicon.json samples/SQL/query.sql || exit

echo '==== FILL'

python3 pysoclz.py fill -p samples/C/lexicon.json samples/C/helloworld2.c.clo 10 || exit

echo '==== SUM'

python3 pysoclz.py sum samples/SQL/query.sql.clo || exit

echo '==== CLEAN'

python3 pysoclz.py clean samples/SQL/query.sql.clo || exit

echo '==== GENERATE'

python3 pysoclz.py generate -p samples/C/helloworld.c.clo HTML -qt samples/question.inc.html || exit
python3 pysoclz.py generate -p samples/C/helloworld.c.clo XML-NUMS -qt samples/question.inc.html || exit
python3 pysoclz.py generate -p samples/C/helloworld.c.clo XML -qt samples/question.inc.html || exit
python3 pysoclz.py generate -p samples/C/helloworld.c.clo XML-NUMS -qt samples/question.inc.html || exit

echo '==== INIT'

python3 pysoclz.py init -p EN XML -qt samples/PHP-HTML/power_exercise.inc.html || exit
python3 pysoclz.py init -p EN HTML -qt samples/PHP-HTML/power_exercise.inc.html || exit

