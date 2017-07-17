<!DOCTYPE html>
<html><head><meta http-equiv="content-type" content="text/html;charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no"/>
</head>
<body>
<script>
var needReq = false;
var isRunning = false;
function search(q){
    if(q.trim().length == 0){
        document.getElementById("list").innerHTML = "";
        return false;
    }
    isRunning = true;
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", "searchbus.php");
    xmlhttp.onreadystatechange = function(){
        if(xmlhttp.readyState == 4){
            isRunning = false;
            if(xmlhttp.status == 200){
                updateLineList(xmlhttp.responseText);
            }
            if(needReq){
                needReq = false;
                search(document.getElementById("search").value);
            }
        }
    }
    var formData = new FormData();
    formData.append('q', q);
    xmlhttp.send(formData);
}
function updateLineList(str){
    var lineList = eval(str);
    var htmlContent = "";
    for(var i=0;i<lineList.length;i++){
        htmlContent += "<div><a href=\"bjbus.php?id="+lineList[i]["id"]+"\" target=\"_blank\">"+lineList[i]["text"]+"</a></div>";
    }
    document.getElementById("list").innerHTML = htmlContent;
}
</script>
<?php
$ids = explode(",", $_GET['id']);
$lineids = array();
foreach($ids as $id){
    if(preg_match("/^\d+$/", $id)){
        $lineids[] = $id;
    }
}
if(count($lineids)){
    $cmd = '/bin/grep -P "^('.implode("|", $lineids).') " /home/nabice/etc/busallline';
    $output = array();
    exec($cmd, $output);
    foreach($output as $line){
        show_real(explode(" ", $line, 2));
    }
}
function show_real($line){
    echo "<pre>";
    echo "<b>{$line[1]}</b>\n";
    $output = array();
    exec("/home/nabice/bin/bjbus {$line[0]}", $output);
    foreach($output as $line){
        $item = explode(",", $line);
        if($item[1] == "-1"){
            echo "到站：<span style=\"color:blue;\">{$item[0]}</span>\n";
        }else{
            echo "距<span style=\"color:blue;\">{$item[0]}</span>还有{$item[1]}米\n";
        }
    }
    echo "</pre>";
}
?>
<input id="search" oninput="if(!isRunning){search(this.value);}else{needReq=true;}"/>
<br/>
<div id="list"></div>
</body>
</html>
