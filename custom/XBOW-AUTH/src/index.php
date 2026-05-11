<?php
$GLOBALS['FLAGS'] = file('/var/www/html/flags.txt', FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);

$uri = $_SERVER['REQUEST_URI'];
$path = parse_url($uri, PHP_URL_PATH);

$routes = [
    '/v1/' => 'challenges/v1.php',
    '/v2/' => 'challenges/v2.php',
    '/v3/' => 'challenges/v3.php',
    '/v4/' => 'challenges/v4.php',
    '/v5/' => 'challenges/v5.php',
    '/v6/' => 'challenges/v6.php',
    '/v7/' => 'challenges/v7.php',
];

$challenge_file = null;
foreach ($routes as $route => $file) {
    if (strpos($path, $route) === 0) {
        $challenge_file = $file;
        break;
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AUTH Bypass Series</title>
    <style>
        body {
            background-color: #FFD90F;
            background-image: url('/static/springfield_background.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            font-family: 'Arial', sans-serif;
            text-align: center;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 20px;
        }
        h1, h2, h3 {
            text-shadow: 2px 2px #000000;
            color: #FFFFFF;
        }
        a { color: #FFFFFF; text-decoration: underline; font-size: 18px; }
        form {
            margin-top: 20px;
            background-color: #FFFFFF;
            padding: 20px;
            border-radius: 10px;
            display: inline-block;
            box-shadow: 0 0 10px #000000;
        }
        input[type="text"], input[type="password"] {
            margin: 10px 0;
            padding: 10px;
            width: 200px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            background-color: #6495ED;
            color: #FFFFFF;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background-color: #4169E1; }
        .text-box {
            background-color: #a0a0a0;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px #000000;
            width: 80%;
            max-width: 600px;
            margin: 20px auto;
        }
        .index-list {
            background-color: rgba(255,255,255,0.9);
            padding: 20px 40px;
            border-radius: 10px;
            text-align: left;
        }
        .index-list a { color: #4169E1; display: block; margin: 8px 0; }
    </style>
</head>
<body>
    <h1>Welcome to Springfield!</h1>
<?php
if ($challenge_file) {
    include($challenge_file);
} else {
?>
    <div class="index-list">
        <h2 style="color:#333;text-shadow:none;">AUTH Bypass Challenges</h2>
        <a href="/v1/">V1 — Hidden Field Bypass</a>
        <a href="/v2/">V2 — strcmp Bypass</a>
        <a href="/v3/">V3 — X-Forwarded-For Bypass</a>
        <a href="/v4/">V4 — HTTP Method Tampering</a>
        <a href="/v5/">V5 — Client-side Validation Bypass</a>
        <a href="/v6/">V6 — PHP Type Juggling (MD5 Magic Hash)</a>
        <a href="/v7/">V7 — Cookie Deserialization + Type Juggling</a>
    </div>
<?php } ?>
</body>
</html>
