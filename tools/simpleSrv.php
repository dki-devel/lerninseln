<?php
header("Access-Control-Allow-Methods: GET, HEAD, POST, PUT, DELETE, CONNECT, OPTIONS, TRACE, PATCH");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: access-control-allow-origin, headers, origin, callback, content-type");
header("Access-Control-Allow-Credentials: true");
header("Content-Type: application/json; charset=UTF-8");
//header("Content-Type: */*;encoding=gzip, deflate, br");
//https://ionicframework.com/docs/troubleshooting/cors

require_once "mlog.php";
require "makeQr.php";
require "pdfGen.php";
require "sendMail.php";

// --------------------------------------------------
// error reasons
// --------------------------------------------------
define("REASON", ["AUTH","KEY","PAY","REQ","SERV","SOLD"]);

// --------------------------------------------------
  // log function
  // --------------------------------------------------

  /*
  define("LOG", "srv.log");
  define("LPRIO", 0); // minimal log priority
  // log function to file
  function mlog($msg, $prio = 0)
  {
      if ($prio >= LPRIO) {
          $ts = date(DATE_RFC2822);
          file_put_contents(LOG, $ts . " : " . $msg . PHP_EOL, FILE_APPEND);
      }
  }
  */


/* fill database paramteres in config.ini */
/*$cfg = parse_ini_file("../../files/iot/config.ini", false);*/
//$cfg = parse_ini_file("/home/akugel/files/lerninseln/config.ini", false);
//$cfg = parse_ini_file("config.ini", false);

// ini file on uberspace is elsewhere
$cfg = array();
//$cfg = parse_ini_file("/home/akugel/files/kdg/kdg.ini",false);
// $cfg = parse_ini_file("kdg.ini",false);
try {
    //	mlog("SRV " . print_r($_SERVER,true));
    if (!isset($_SERVER['HTTP_HOST']) or !isset($_SERVER['HTTPS'])) {
        $cfg = parse_ini_file("config.ini", false);
        $cfg["local"] = true;
        mlog("Local config");
    } else {
        // uberspace
        $cfg = parse_ini_file("/home/akugel/files/lerninseln/config.ini", false);
        //$cfg = parse_ini_file("news.ini", false);
        $cfg["local"] = false;
        mlog("Host config");
    }
} catch (Exception $e) {
    die("Config Error");
}


$meth = $_SERVER["REQUEST_METHOD"];
mlog("Method: " . $meth);

$result = array();
$mailing = array("request" => 0);

switch ($meth) {
    case "GET":
        mlog("GET");
        $parms = array("table" => FILTER_SANITIZE_STRING);
        $args = filter_input_array(INPUT_GET, $parms, true);

        if ($args & ($args["table"] !== null)) {
            $table = $args["table"];
        }
        
        define("TABLES", array("config","provider","category","audience","event","ticket","code"));
        
        if (array_search($table, TABLES) === false) {
            mlog("Invalid table");
            header("HTTP/1.1 400 Bad request");
        } else {
            try {
                // setting utf-8 here is IMPORTANT !!!!
                $pdo = new PDO(
                    'mysql:host=' . $cfg["dbserv"] . ';dbname=' . $cfg["dbname"],
                    $cfg["dbuser"],
                    $cfg["dbpass"],
                    array(PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8")
                );
            } catch (Exception $e) {
                mlog("DB error", 9);
                die("DB Error");
            }
            
            $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
            /* $query = "SELECT * from sensors order by `index` asc"; */
            /*$query = "SELECT id,count,co2,bat,pres,hum,temp,light,rssi,rfu,date,pkt,rep from sensors order by `index` asc"; */
            
            $query = "SELECT * from " . $table;
            
            $statement = $pdo->query($query);
            
            foreach ($statement as $row) {
                //echo("row").PHP_EOL;
                //print_r($row);
                array_push($result, $row);
            }
        }
        break;

    case "POST":
        mlog("POST");
        $input = json_decode(file_get_contents('php://input'), true);
        mlog("Input: " . json_encode($input));
        // we expect a request type and a payload
        if (!(array_key_exists("request", $input)) || !(array_key_exists("payload", $input))) {
            mlog("Keys missing");
            $result = array("payload" => array("reason" => REASON[1]),"status" => 0);
            break;
        }
        $task = $input["request"];
        $payload = $input["payload"];
        switch ($task) {
            case 1:
                if (!(array_key_exists("ticket", $payload)) || !(array_key_exists("email", $payload))) {
                    mlog("Req 1 keys missing");
                    $result = array("payload" => array("reason" => REASON[1]),"status" => 0);
                    $task = 0; // clear request to indicate error
                    break;
                }
                mlog("processing req 1");
                $mailing["request"] = $task;
                $mailing["payload"] = $payload;
                $result = array("payload" => array("data" => "OK1"),"status" => 1);
                break;
            case 2:
                if (!(array_key_exists("ticket", $payload))
                    || !(array_key_exists("email", $payload))
                    || !(array_key_exists("code", $payload))
                ) {
                    mlog("Req 2 keys missing");
                    $result = array("payload" => array("reason" => REASON[1]),"status" => 0);
                    $task = 0; // clear request to indicate error
                    break;
                }
                mlog("processing req 2");
                
                $to = "ak@akugel.de";
                $event = array();
                $event["name"] = "Extra Veranstaltung";
                $event["date"] = "2021-07-20";
                $event["time"] = "19:00";
                $event["count"] = "1";
                $event["location1"] = "Digitallabor Rathaus Karlsruhe";
                $event["location2"] = "Markplatz, Karlsruhe";
                $qr = makeQr( hash("sha256","test123"));
                $event["qrdata"] = $qr;
                $logo = file_get_contents("logo.jpg", false); //, stream_context_create($opciones_ssl));
                $logo_base_64 = base64_encode($logo);
                $event["logo"] = 'data:image/jpeg;base64,' . $logo_base_64;
                $bg = file_get_contents("bg.jpg", false); //, stream_context_create($opciones_ssl));
                $bg_base_64 = base64_encode($bg);
                $event["bg"] = 'data:image/jpeg;base64,' . $bg_base_64;
            
                $pdf = pdfGen($event);
                $subj = "Dein Lerninsel Ticket";
                $msg = "Vielen Dank, dass Du an unserer Veranstaltung teilnimmst. Hier ist Dein Ticket." . PHP_EOL. PHP_EOL;
                $msg .= "Du kannst es ausdrucken und mitbringen. Oder das Ticket auf Deinem Smartphone anzeigen."  . PHP_EOL;
                $msg .=  PHP_EOL . "--" . PHP_EOL . "Das Lerninsel Team"  . PHP_EOL;
                $r = sendSmtp($cfg,$to, $subj, $msg, $pdf);
                mlog("Send ticket returned " . $r);
                $result = array("payload" => array("data" => "OK2","qr" => $qr),"status" => 1);
                break;
            default:
                mlog("Invalid request");
                $result = array("payload" => array("reason" => REASON[4]),"status" => 0);
                $task = 0; // clear request to indicate error
                break;
        }
        break;

    default:
        mlog("Other");
        break;
}

echo json_encode($result);
ob_end_flush();

if ($mailing["request"] > 0) {
    // acquire lock
    //$lock = "/var/www/virtual/akugel/html/lerninseln/lock.txt";
    // don't echo anything here!
    // might need to create lockfile beforehand
    $lock = "lock.txt";
    $fp = fopen($lock, "r+");
    if (flock($fp, LOCK_EX)) { // exklusive Sperre
        ftruncate($fp, 0); // k??rze Datei
        //$handle = popen('./a.php 2>&1', 'w');
        // strangely, this does not work with exec ...
        $w = json_encode(array("data" => "aslslfq??lwfmq??"));
        fputs($fp, $w);
        fflush($fp);
        $h = popen('./bgpipe.php & >/dev/null', 'w');
        fwrite($h,"test");
        fclose($h);
        flock($fp, LOCK_UN); // Gib Sperre frei
    } else {
        mlog("Lock failed",9);
    }

    fclose($fp);
}


/*
ob_end_flush();

if ($forked) {
    mlog("wait for " . $child);
    //ob_clean(); //end_flush();
    //ob_end_clean(); //end_flush();
    pcntl_waitpid($child,$status); //option NOHANG: non blocking
    //pcntl_wait($status); //option NOHANG: non blocking
    mlog("wait end");
}
*/
