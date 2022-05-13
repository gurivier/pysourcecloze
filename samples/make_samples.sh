#!/bin/sh

# C example (HTML and XML)

python3 ../pysoclz.py generate C/helloworld.c.clo HTML-NUMS -qt question.inc.html
python3 ../pysoclz.py generate C/helloworld.c.clo XML-NUMS -qt question.inc.html

# SQL example (HTML and XML)

python3 ../pysoclz.py generate SQL/query.sql.clo HTML-NUMS -qt PHP-HTML/power_question1.inc.html
python3 ../pysoclz.py generate SQL/query.sql.clo XML-NUMS -qt PHP-HTML/power_question2.inc.html

# PHP-HTML example (XML only)

cd PHP-HTML

python3 ../../pysoclz.py init EN XML -qt power_exercise.inc.html -ei
python3 ../../pysoclz.py generate power.html.clo XML-NUMS -qt power_question1.inc.html
python3 ../../pysoclz.py generate power.php.clo XML-NUMS -qt power_question2.inc.html

cd ..

# Init example (HTML and XML)

python3 ../pysoclz.py init EN HTML
python3 ../pysoclz.py init EN XML
