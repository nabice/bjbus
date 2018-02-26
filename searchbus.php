<?php
$output = array();
$lines = file("/home/nabice/etc/busallline");
for($i=0; $i<count($lines); $i++){
    $lineInfo = explode(" ", $lines[$i], 2);
    if(strpos($lineInfo[1], $_POST['q']) !== FALSE){
        $output[] = array("id"=>$lineInfo[0], "text"=>$lineInfo[1]);
    }
}
sort($output);
echo json_encode($output);
?>
