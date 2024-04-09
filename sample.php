<!--


Patterns:
- Source: _GET ==> Filters:[]
- Sanitization: nosanitization ==> Filters:[]
- Filters complete: Filters:[]
- Dataflow: global_variable
- Context: xss_plain
- Sink: echo_func

State:
- State: Bad
- Exploitable: Yes


1. Create script tag with <script>
-->
<?php


$tainted = $_GET;
$tainted = $tainted["t"];
$sanitized = $tainted;
function setGlobal($var)
{
  global $g;
  $g = $var;
}
function getGlobal()
{
  global $g;
  return $g;
}
setGlobal($sanitized);
$dataflow = getGlobal();
$context = ("Hello" . $dataflow);
echo($context);

?>