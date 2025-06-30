<?php
if (isset($_GET['file'])) {
    $file = __DIR__ . "/" . basename($_GET['file']); // Secure path

    if (file_exists($file)) {
        // Set headers to force download
        header('Content-Type: application/pdf');
        header('Content-Disposition: attachment; filename="' . basename($file) . '"');
        header('Content-Length: ' . filesize($file));

        // Read the file and output it
        readfile($file);
        exit;
    } else {
        die("Error: File not found!");
    }
} else {
    die("Error: No file specified!");
}
?>
