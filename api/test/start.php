<?php
header("Content-Type: application/json");
include "../../db.php";

$data = json_decode(file_get_contents("php://input"), true);
$user_id   = $data['user_id'] ?? null;
$test_type = $data['test_type'] ?? null;

if (!$user_id || !$test_type) {
    echo json_encode([
        "status" => false,
        "error" => "user_id and test_type are required"
    ]);
    exit;
}

// Validate test type
$allowed = ['RAN', 'VRG', 'PUR'];
if (!in_array($test_type, $allowed)) {
    echo json_encode([
        "status" => false,
        "error" => "Invalid test_type: $test_type"
    ]);
    exit;
}

$stmt = $conn->prepare("
    INSERT INTO tests (user_id, test_type, started_at, status, total_samples)
    VALUES (?, ?, NOW(), 'running', 0)
");

$stmt->bind_param("is", $user_id, $test_type);

if ($stmt->execute()) {
    $test_id = $stmt->insert_id;
    
    // Return response with duration (in seconds) based on test type
    $duration = 180; // Default 3 minutes
    if ($test_type === 'VRG') {
        $duration = 120; // 2 minutes for Quick Screening
    } elseif ($test_type === 'PUR') {
        $duration = 300; // 5 minutes for Full Assessment
    }
    
    echo json_encode([
        "status" => true,
        "test_id" => $test_id,
        "duration" => $duration,
        "message" => "Test started"
    ]);
} else {
    echo json_encode([
        "status" => false,
        "error" => $stmt->error
    ]);
}
?>
