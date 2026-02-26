<?php
header("Content-Type: application/json");
include "../../db.php";

$data = json_decode(file_get_contents("php://input"), true);

$test_id = $data['test_id'] ?? null;
$n = $data['n'] ?? null;
$x = $data['x'] ?? null;
$y = $data['y'] ?? null;
$lx = $data['lx'] ?? null;
$ly = $data['ly'] ?? null;
$rx = $data['rx'] ?? null;
$ry = $data['ry'] ?? null;

// Validate required fields
if ($test_id === null || $n === null || $x === null || $y === null || 
    $lx === null || $ly === null || $rx === null || $ry === null) {
    echo json_encode([
        "status" => false,
        "error" => "All fields are required: test_id, n, x, y, lx, ly, rx, ry"
    ]);
    exit;
}

// Insert eye data sample
$stmt = $conn->prepare("
    INSERT INTO eye_data (test_id, n, x, y, lx, ly, rx, ry)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
");

$stmt->bind_param("iidddddd", $test_id, $n, $x, $y, $lx, $ly, $rx, $ry);

if ($stmt->execute()) {
    // Update total_samples count in tests table
    $update = $conn->prepare("UPDATE tests SET total_samples = total_samples + 1 WHERE id = ?");
    $update->bind_param("i", $test_id);
    $update->execute();
    
    echo json_encode([
        "status" => true,
        "message" => "Eye data sample saved"
    ]);
} else {
    echo json_encode([
        "status" => false,
        "error" => $stmt->error
    ]);
}
?>
