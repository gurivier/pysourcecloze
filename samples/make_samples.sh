#!/bin/sh

# C example (HTML and XML)

python3 ../pysoclz.py generate C/helloworld.c.clo HTML-NUMS -qt question.inc.html
python3 ../pysoclz.py generate C/helloworld.c.clo XML-NUMS -qt question.inc.html

# SQL example (HTML and XML)

python3 ../pysoclz.py generate SQL/query.sql.clo HTML-NUMS -qt PHP-HTML/power_question1.inc.html
python3 ../pysoclz.py generate SQL/query.sql.clo XML-NUMS -qt PHP-HTML/power_question2.inc.html

# PHP-HTML example (XML only)

python3 ../pysoclz.py init EN XML -qt PHP-HTML/power_exercise.inc.html
python3 ../pysoclz.py generate PHP-HTML/power.html.clo XML-NUMS -qt PHP-HTML/power_question1.inc.html
python3 ../pysoclz.py generate PHP-HTML/power.php.clo XML-NUMS -qt PHP-HTML/power_question2.inc.html

# Init example (HTML and XML)

python3 ../pysoclz.py init EN HTML
python3 ../pysoclz.py init EN XML
