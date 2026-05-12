<!DOCTYPE html>
<html>
<head><title>Document Management System</title></head>
<body>
<h1>Document Management System</h1>
<h2>Upload Document</h2>
<form method="POST" action="upload.php" enctype="multipart/form-data">
  <input type="file" name="document">
  <button type="submit">Upload</button>
</form>
<p><small>Allowed: .doc, .docx, .pdf, .txt, .jpg, .png</small></p>
</body>
</html>
