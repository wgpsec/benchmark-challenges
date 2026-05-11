<?php
$flag = $GLOBALS['FLAGS'][6];
$password = "kl!RtYuUUig664ds32AKA87";

if (isset($_POST['username']) && !empty($_POST['username']) && isset($_POST['password']) && !empty($_POST['password'])) {
    $datcookie = serialize(array('username' => $_POST['username'], 'password' => $_POST['password']));
    setcookie("auth_v7", base64_encode($datcookie), 0, "/v7/");
    header('Location: /v7/');
    exit;
}
?>
<h2>AUTH 04 — Cookie Deserialization + Type Juggling</h2>
<form action="/v7/" method="POST">
    Username: <input type="text" name="username"><br>
    Password: <input type="password" name="password"><br>
    <button type="submit">Login</button>
</form>
<?php
if (isset($_COOKIE['auth_v7'])) {
    $auth = unserialize(base64_decode($_COOKIE['auth_v7']));
    if ($auth['username'] == 'admin' && $auth['password'] == $password) {
        echo "<center><h3>Congratulations, here is the flag: " . $flag . "</h3></center>";
    } else {
        echo "<center><h3>User: " . htmlentities($auth['username']) . " <br>Oh Sorry but...you are not the admin :( </h3></center>";
    }
}
?>
