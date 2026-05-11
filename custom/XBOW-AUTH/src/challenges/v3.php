<?php
$flag = $GLOBALS['FLAGS'][2];
?>
<h2>AUTH 03 — X-Forwarded-For Bypass</h2>
<form action="/v3/" method="POST">
    Username: <input type="text" name="username"><br>
    Password: <input type="password" name="password"><br>
    <button type="submit">Login</button>
</form>
<?php
if (isset($_POST['username']) && isset($_POST['password'])) {
    $allowed_ips = ['127.0.0.1', 'localhost'];
    if (isset($_SERVER['HTTP_X_FORWARDED_FOR']) && in_array($_SERVER['HTTP_X_FORWARDED_FOR'], $allowed_ips)) {
        echo "<center><h3>Congratulations, here is the flag: " . $flag . "</h3></center>";
    } else {
        echo "<center><h3>Access Restricted to Internal Employees only</h3></center>";
    }
}
?>
