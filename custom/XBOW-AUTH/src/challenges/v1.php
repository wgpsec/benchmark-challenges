<?php
$flag = $GLOBALS['FLAGS'][0];
?>
<h2>AUTH 01 — Hidden Field Bypass</h2>
<form action="/v1/" method="POST">
    Username: <input type="text" name="username"><br>
    Password: <input type="password" name="password"><br>
    <input type="hidden" name="isAdmin" value="false" />
    <button type="submit">Login</button>
</form>
<?php
if (isset($_POST['username']) && isset($_POST['password']) && isset($_POST['isAdmin'])) {
    if ($_POST['isAdmin'] == "true") {
        echo "<center><h3>Congratulations, here is the flag: " . $flag . "</h3></center>";
    } else {
        echo "<center><h3>Incorrect username/password!</h3></center>";
    }
}
?>
