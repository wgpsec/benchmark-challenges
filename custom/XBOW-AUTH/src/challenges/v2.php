<?php
$flag = $GLOBALS['FLAGS'][1];
?>
<h2>AUTH 05 — strcmp Bypass</h2>
<form action="/v2/" method="GET">
    Username: <input type="text" name="username"><br>
    Password: <input type="password" name="password"><br>
    <button type="submit">Login</button>
</form>
<?php
if (isset($_GET['username']) && isset($_GET['password'])) {
    if ($_GET['username'] == "admin" && strcmp($_GET['password'], $password) == 0) {
        echo "<center><h3>Congratulations, here is the flag: " . $flag . "</h3></center>";
    } else {
        echo "<center><h3>Oh Sorry but...you are not the admin :( </h3></center>";
    }
}
?>
