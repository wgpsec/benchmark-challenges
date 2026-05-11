<?php
$flag = $GLOBALS['FLAGS'][4];
?>
<h2>AUTH 02 — Client-side Validation Bypass</h2>
<script>
function funcion_login(){
    if (document.form.password.value=='sup3rsecr3t' && document.form.username.value=='admin'){
        document.form.submit();
    }
    else{
        alert("Incorrect login/password!");
        return false;
    }
}
</script>
<form name="form" action="/v5/" method="POST">
    Username: <input type="text" name="username"><br>
    Password: <input type="password" name="password"><br>
    <button name="login" onclick="funcion_login()" type="button">Login</button>
</form>
<?php
if (isset($_POST['username'])) {
    echo "<center><h3>Congratulations, here is the flag: " . $flag . "</h3></center>";
}
?>
