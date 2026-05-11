<?php
$flag = $GLOBALS['FLAGS'][3];
?>
<h2>AUTH 07 — HTTP Method Tampering</h2>
<div class="text-box">
    <p>This page is only accessible via the correct HTTP method. The login form uses GET, but the flag requires a different approach.</p>
</div>
<form action="/v4/" method="GET">
    Username: <input type="text" name="username"><br>
    Password: <input type="password" name="password"><br>
    <button type="submit">Login</button>
</form>
<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    echo "<center><h3>Congratulations, here is the flag: " . $flag . "</h3></center>";
}
?>
