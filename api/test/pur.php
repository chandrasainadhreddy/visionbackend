<?php
header("Content-Type: application/json");
include "../../db.php";

$data = json_decode(file_get_contents("php://input"), true);
$test_id = $data['test_id'] ?? null;

if (!$test_id) {
    echo json_encode([
        "status" => false,
        "error" => "test_id is required"
    ]);
    exit;
}

// Get test info
$stmt = $conn->prepare("SELECT test_type, user_id FROM tests WHERE id = ?");
$stmt->bind_param("i", $test_id);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows === 0) {
    echo json_encode([
        "status" => false,
        "error" => "Test not found"
    ]);
    exit;
}

$test = $result->fetch_assoc();
$test_type = $test['test_type'];

// Call Flask AI server
$flask_url = "http://127.0.0.1:5000/analyze";
$flask_data = json_encode([
    "test_id" => $test_id,
    "test_type" => $test_type
]);

$ch = curl_init($flask_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $flask_data);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curl_error = curl_error($ch);
curl_close($ch);

if ($curl_error) {
    echo json_encode([
        "status" => false,
        "error" => "Failed to connect to AI server: " . $curl_error
    ]);
    exit;
}

if ($http_code !== 200) {
    echo json_encode([
        "status" => false,
        "error" => "AI server error: HTTP $http_code"
    ]);
    exit;
}

$ai_result = json_decode($response, true);

if (!$ai_result || !isset($ai_result['classification']) || !isset($ai_result['score'])) {
    echo json_encode([
        "status" => false,
        "error" => "Invalid AI response"
    ]);
    exit;
}

// Save result to database
$classification = $ai_result['classification'];
$score = $ai_result['score'];
$ai_notes = $ai_result['notes'] ?? '';

$stmt = $conn->prepare("
    INSERT INTO results (test_id, classification, score, ai_notes)
    VALUES (?, ?, ?, ?)
");
$stmt->bind_param("isds", $test_id, $classification, $score, $ai_notes);
$stmt->execute();

// Update test status
$stmt = $conn->prepare("UPDATE tests SET status = 'completed' WHERE id = ?");
$stmt->bind_param("i", $test_id);
$stmt->execute();

// Map classification to severity
$severity = "Normal";
if (strpos(strtolower($classification), 'mild') !== false) {
    $severity = "Mild";
} elseif (strpos(strtolower($classification), 'attention') !== false || 
          strpos(strtolower($classification), 'severe') !== false) {
    $severity = "Severe";
}

// Generate description based on test type and severity
$descriptions = [
    "RAN" => [
        "Normal" => "Your gaze stability is normal.",
        "Mild" => "Slight eye drift detected during fixation.",
        "Severe" => "Poor fixation stability detected."
    ],
    "VRG" => [
        "Normal" => "Your binocular coordination is healthy.",
        "Mild" => "Minor eye coordination mismatch detected.",
        "Severe" => "Significant binocular coordination issue detected."
    ],
    "PUR" => [
        "Normal" => "Your eye movement control is within normal limits.",
        "Mild" => "Minor delay observed during rapid eye movements.",
        "Severe" => "Reduced eye movement control detected."
    ]
];

$description = $descriptions[$test_type][$severity] ?? "Analysis completed.";

// Return response matching TestResultResponse model
echo json_encode([
    "test_type" => $test_type,
    "score" => $score,
    "severity" => $severity,
    "description" => $description,
    "metrics" => $ai_result['metrics'] ?? []
]);
?>
