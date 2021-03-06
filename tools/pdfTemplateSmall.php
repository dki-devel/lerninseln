<!DOCTYPE html>
<html>
<head>
<style>
/* default dpi is 72.
A$ size is 8.3 * 11.7 inch 
= 600 * 840pt

resolution can be changed by 
$dompdf->set_option( 'dpi' , '200' );

dpi maybe only affects px settings, but not pt settings
fixed resolution of a PDF, which is 72 PT per inch. 
*/

body {
    font-family: sans-serif;
    width:520pt;
    background-image: url(<?php echo $event["bg"];?>);
    background-repeat: no-repeat;
    /*background-attachment: fixed; */ 
    /* background-size: contain; */
    background-size: 520pt 270pt;
    /* <a href="https://www.freepik.com/photos/background">Background photo created by mrsiraphol - www.freepik.com</a> */

}
h2 {
    line-height: 20pt;
    font-size: 16pt;
    margin-bottom: 0;
    padding: 0;
    padding-left:10pt;
}
p {
    font-size:12pt;
    line-height: 14pt;
    padding-top: 2pt;
    padding-bottom: 2pt;
    padding-left:10pt;
}


.bold {
    font-weight: 700;
    font-family: sans-serif;
    color: rgb(255,0,0);
}

.date {
    margin-bottom: 4pt;
}
/*
.bg {
    background-color: rgba(220,220,220,.5);
}
*/
#back {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 320pt;
    background: rgba(240,240,240,.8);
}
#header {
    position: absolute;
    top: 0pt;
    left: 0pt;
}

#logo {
    position: absolute;
    top: 20pt;
    left: 440pt;
    width:80pt;
}

#event {
    position: absolute;
    top:80pt;
    left:0;
}

#qr {
    position: fixed;
    top: 80pt;
    left: 280pt;
    width: 196pt;
    border: solid 2pt;
    background-color: rgb(255,255,255);
    padding: 20pt;
}


#footer {
    position: absolute;
    top: 270pt;
    left: 0;
    width:100%;
    height: 30pt;
    padding-top:0pt;
    padding-bottom:18pt;
    background-color: rgba(200,240,200,.5);
    border-top: solid 2pt rgb(0,0,0);
}

#attribution {
    position: absolute;
    top: 294pt;
    left: 0;
    padding-top:0;
    padding-bottom:0;
    font-size: 8pt;
    color: rgb(100,100,100);
}

h1 {
    line-height: 30pt;
    font-size: 24pt;
    color: rgb(0,0,255);
}


</style>
</head>
<body>

<div id="back">
<h1 id="header" >Lerninseln Karlsruhe</h1>
<img id="logo" src="<?php echo $event["logo"];?>" class="logo">

<div id="event" class="bg">
    <h2>Ticket f??r die Veranstaltung:</h2>
    <h2><span class="bold"><?php echo $event["name"];?></span></h2>
    <p class="date">Datum <?php echo $event["date"];?>, 
        <?php echo $event["time"];?> Uhr
        </p>
        <p> 
        <?php echo $event["location1"];?>
        <br>
        <?php echo $event["location2"];?>
        </p>
        <p> 
        <?php echo $event["count"];?> Persone(n)
        </p>
</div>

<div id="footer" class="bg">
<p >Wir freuen uns auf Dich</p>
</div>
<p id="attribution">
Background photo created by mrsiraphol - www.freepik.com
</p>

<img id="qr" src="<?php echo $event["qrdata"];?>">

</body>
</html>
