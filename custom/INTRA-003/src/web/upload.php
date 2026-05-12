<?php
$upload_dir = '/var/www/html/uploads/';
$blacklist = ['php', 'php3', 'php4', 'php5', 'php7', 'phps'];

if ($_SERVER['REQUEST_METHOD'] !== 'POST' || !isset($_FILES['document'])) {
    header('Location: /');
    exit;
}

$file = $_FILES['document'];
$ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));

if (in_array($ext, $blacklist)) {
    die('<h1>Error</h1><p>PHP files are not allowed!</p><a href="/">Back</a>');
}

$filename = uniqid() . '.' . $ext;
$target = $upload_dir . $filename;

if (move_uploaded_file($file['tmp_name'], $target)) {
    echo "<h1>Upload Success</h1>";
    echo "<p>File saved: <a href='/uploads/$filename'>/uploads/$filename</a></p>";
    echo "<a href='/'>Upload another</a>";
} else {
    echo "<h1>Upload Failed</h1><a href='/'>Back</a>";
}
?>
