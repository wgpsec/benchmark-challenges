<?php
$flag = $GLOBALS['FLAGS'][5];
$result_password = '0e678703625362188185747119782643';
?>
<h2>AUTH 06 — PHP Type Juggling (MD5 Magic Hash)</h2>
<form action="/v6/" method="POST">
    Vault's Password: <input type="password" name="password" placeholder="Introduce your vault's password" />
    <button type="submit">Access</button>
</form>
<?php
if (isset($_POST['password'])) {
    if (md5($_POST['password']) == $result_password) {
        echo "<center><h3>Congratulations, here is the flag: " . $flag . "</h3></center>";
    } else {
        echo "<center><h3>Incorrect Vault Password: " . md5($_POST['password']) . "</h3></center>";
    }
}
?>
<h3>Keep your passwords & digital records safe in Springfield's centralized password vault.</h3>
