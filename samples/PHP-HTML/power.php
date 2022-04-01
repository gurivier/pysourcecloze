<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Power</title>
    </head>
    <body>
        <h1>Power</h1>
        <?php
        
        function show($text, $val, $unit) {
            echo '<p>'.$text.' = '.$val.' '.$unit.'</p>' ;
        }
        
        $factor = ($_POST['unit'] == 'mA') ? .001 : 1 ;
        
        $V = $_POST['voltage'] ;
        $I = $_POST['current'] * $factor ;
        $P = $V * $I ;
        
        show('Voltage', $V, 'V') ;
        show('Current', $I, 'A') ;
        show('Power', $P, 'W') ;
        
        ?>
        <p><a href="power.html">Do it again</a></p>
    </body>
</html>

