<?php
  // log function to file
  define("LPRIO", 0); // minimal log priority
  define("LOG", "srv.log");

  function mlog($msg, $prio = 0)
  {
      if ($prio >= LPRIO) {
          $ts = date(DATE_RFC2822);
          file_put_contents(LOG, $ts . " : " . $msg . PHP_EOL, FILE_APPEND);
      }
  }

?>

