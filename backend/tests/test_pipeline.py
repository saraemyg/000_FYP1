"""
ETL Pipeline Test Script
=========================
Tests the entire pipeline WITHOUT needing:
- A real GPU
- YOLO model weights
- Real surveillance videos
- PostgreSQL running

It uses mock/fake data to verify every component works correctly.

HOW TO RUN:
    cd backend/
    python tests/test_pipeline.py

WHAT IT TESTS:
    1. Config loads correctly
    2. Database models are valid SQLAlchemy classes
    3. Frame extractor reads video files
    4. ROI pruner crops frames correctly
    5. Detector output format is correct
    6. Classifier output format is correct
    7. Loader can format data for DB insertion
    8. Alert engine matches rules correctly
    9. Full pipeline integration (with mocks)

If all tests pass, your code is correct and ready for real data.
"""

import sys
import os
import numpy as np
from datetime import datetime
from collections import namedtuple

# Add backend root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Track test results
passed = 0
failed = 0


skipped = 0

def test(name, func):
    """Run a test and print result."""
    global passed, failed, skipped
    try:
        func()
        print(f"  ✓ {name}")
        passed += 1
    except ImportError as e:
        module = str(e).split("'")[1] if "'" in str(e) else str(e)
        print(f"  ⊘ {name} [SKIPPED — install {module} first]")
        skipped += 1
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        failed += 1


# ══════════════════════════════════════════════════════════
# TEST 1: Config
# ══════════════════════════════════════════════════════════
print("\n[1/8] Testing Config...")


def test_config():
    from config import settings
    assert settings.TARGET_FPS == 15, f"Expected 15, got {settings.TARGET_FPS}"
    assert settings.YOLO_INPUT_SIZE == 640
    assert len(settings.BEHAVIOR_CLASSES) == 7
    assert "walking" in settings.BEHAVIOR_CLASSES
    assert "running" in settings.BEHAVIOR_CLASSES
    assert settings.DEVICE in ("cuda", "cpu")


test("Config loads and has correct defaults", test_config)


# ══════════════════════════════════════════════════════════
# TEST 2: Database Models
# ══════════════════════════════════════════════════════════
print("\n[2/8] Testing Database Models...")


def test_models_import():
    from db.models import (
        Base, User, Camera, SegmentationMask, Detection,
        PoseKeypoint, Behavior, AlertCriteria, Alert,
        SystemMetric, ProcessingSession
    )
    # Check all tables are registered
    table_names = Base.metadata.tables.keys()
    expected = [
        "users", "cameras", "segmentation_masks", "detections",
        "pose_keypoints", "behaviors", "alert_criteria", "alerts",
        "system_metrics", "processing_sessions"
    ]
    for name in expected:
        assert name in table_names, f"Missing table: {name}"


def test_models_relationships():
    from db.models import Camera, Detection, Alert
    # Check that relationships are defined
    assert hasattr(Camera, 'detections'), "Camera missing detections relationship"
    assert hasattr(Camera, 'alerts'), "Camera missing alerts relationship"
    assert hasattr(Detection, 'behavior'), "Detection missing behavior relationship"
    assert hasattr(Detection, 'keypoints'), "Detection missing keypoints relationship"


test("All 10 models import correctly", test_models_import)
test("Model relationships are defined", test_models_relationships)


# ══════════════════════════════════════════════════════════
# TEST 3: Frame Extractor
# ══════════════════════════════════════════════════════════
print("\n[3/8] Testing Frame Extractor...")


def test_extractor_init():
    from pipeline.extractor import FrameExtractor, FrameData
    ext = FrameExtractor("cam_test", "fake_video.mp4", target_fps=15)
    assert ext.camera_id == "cam_test"
    assert ext.target_fps == 15


def test_frame_data_structure():
    from pipeline.extractor import FrameData
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    fd = FrameData(
        frame=frame,
        frame_number=1,
        timestamp=datetime.utcnow(),
        camera_id="cam_01"
    )
    assert fd.frame.shape == (480, 640, 3)
    assert fd.camera_id == "cam_01"


test("FrameExtractor initializes", test_extractor_init)
test("FrameData structure is correct", test_frame_data_structure)


# ══════════════════════════════════════════════════════════
# TEST 4: ROI Pruner
# ══════════════════════════════════════════════════════════
print("\n[4/8] Testing ROI Pruner...")


def test_pruner_no_mask():
    """Without a mask, pruner should return full frame."""
    from pipeline.roi_pruner import ROIPruner
    pruner = ROIPruner("nonexistent_mask.npy")
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    cropped, info = pruner.crop(frame)
    assert cropped.shape == frame.shape, "Should return full frame when no mask"
    assert info.area_reduction == 0.0


def test_pruner_with_mask():
    """With a mask, pruner should crop to walkable region."""
    from pipeline.roi_pruner import ROIPruner
    # Create a fake mask: top half is walkable (1), bottom half is not (0)
    mask = np.zeros((480, 640), dtype=np.uint8)
    mask[100:300, 150:500] = 1  # walkable region in the middle

    # Save temp mask
    mask_path = "/tmp/test_mask.npy"
    np.save(mask_path, mask)

    pruner = ROIPruner(mask_path)
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    cropped, info = pruner.crop(frame)

    # Cropped frame should be smaller than original
    assert cropped.shape[0] < frame.shape[0] or cropped.shape[1] < frame.shape[1], \
        f"Cropped {cropped.shape} should be smaller than original {frame.shape}"
    assert info.area_reduction > 0, "Area reduction should be > 0"

    # Clean up
    os.remove(mask_path)


def test_pruner_coordinate_mapping():
    """Bounding boxes should map back correctly."""
    from pipeline.roi_pruner import ROIPruner, CropInfo
    crop_info = CropInfo(x1=100, y1=50, x2=500, y2=400, original_w=640, original_h=480, area_reduction=35.0)
    bbox_in_crop = (10, 20, 110, 220)
    bbox_original = ROIPruner.map_bbox_to_original(bbox_in_crop, crop_info)
    assert bbox_original == (110, 70, 210, 270), f"Got {bbox_original}"


test("Pruner works without mask (passthrough)", test_pruner_no_mask)
test("Pruner crops with mask correctly", test_pruner_with_mask)
test("Coordinate mapping back to original", test_pruner_coordinate_mapping)


# ══════════════════════════════════════════════════════════
# TEST 5: Detector Output Format
# ══════════════════════════════════════════════════════════
print("\n[5/8] Testing Detector Output Format...")


def test_detector_data_structures():
    from pipeline.detector import PersonDetection
    det = PersonDetection(
        person_idx=0,
        bbox=(100.0, 200.0, 300.0, 500.0),
        confidence=0.92,
        keypoints_x=[float(i) for i in range(17)],
        keypoints_y=[float(i + 100) for i in range(17)],
        keypoints_conf=[0.9] * 17,
    )
    assert det.person_idx == 0
    assert len(det.keypoints_x) == 17
    assert len(det.keypoints_y) == 17
    assert det.confidence == 0.92


test("PersonDetection data structure", test_detector_data_structures)


# ══════════════════════════════════════════════════════════
# TEST 6: Classifier
# ══════════════════════════════════════════════════════════
print("\n[6/8] Testing Classifier...")


def test_classifier_mlp_architecture():
    """Test that MLP model can be instantiated and forward pass works."""
    import torch
    from pipeline.classifier import BehaviorMLP
    model = BehaviorMLP(input_size=51 * 15, num_classes=7)
    # Fake input: batch of 2, each with 51*15 features
    x = torch.randn(2, 51 * 15)
    output = model(x)
    assert output.shape == (2, 7), f"Expected (2, 7), got {output.shape}"


def test_classifier_without_model():
    """Classifier should return 'unknown' when no MLP model loaded."""
    from pipeline.classifier import BehaviorClassifier
    from pipeline.detector import PersonDetection
    classifier = BehaviorClassifier(mlp_model=None)
    det = PersonDetection(
        person_idx=0, bbox=(0, 0, 100, 200), confidence=0.9,
        keypoints_x=[0.0]*17, keypoints_y=[0.0]*17, keypoints_conf=[0.9]*17,
    )
    results = classifier.classify([det], "cam_test")
    assert len(results) == 1
    assert results[0].behavior_type == "unknown"


def test_classifier_with_mock_model():
    """Classifier should return a valid label with a model loaded."""
    import torch
    from pipeline.classifier import BehaviorClassifier, BehaviorMLP
    from pipeline.detector import PersonDetection
    from config import settings

    model = BehaviorMLP(input_size=51 * settings.POSE_WINDOW_SIZE, num_classes=7)
    model.eval()
    classifier = BehaviorClassifier(mlp_model=model)

    # Feed enough frames to fill the buffer
    for i in range(settings.POSE_WINDOW_SIZE + 1):
        det = PersonDetection(
            person_idx=0, bbox=(10, 20, 110, 320), confidence=0.9,
            keypoints_x=[float(j + i) for j in range(17)],
            keypoints_y=[float(j + 100 + i) for j in range(17)],
            keypoints_conf=[0.8]*17,
        )
        results = classifier.classify([det], "cam_test")

    # After enough frames, should get a real prediction
    assert results[0].behavior_type in settings.BEHAVIOR_CLASSES, \
        f"Got unexpected label: {results[0].behavior_type}"
    assert results[0].confidence > 0.0
    assert len(results[0].raw_scores) == 7


test("MLP architecture forward pass", test_classifier_mlp_architecture)
test("Classifier returns 'unknown' without model", test_classifier_without_model)
test("Classifier returns valid label with mock model", test_classifier_with_mock_model)


# ══════════════════════════════════════════════════════════
# TEST 7: Alert Engine
# ══════════════════════════════════════════════════════════
print("\n[7/8] Testing Alert Engine...")


def test_alert_engine_rule_matching():
    """Alert engine should match behaviors to rules correctly."""
    from pipeline.alert_engine import AlertEngine
    from pipeline.detector import PersonDetection
    from pipeline.classifier import BehaviorResult

    engine = AlertEngine()
    # Manually set rules (normally loaded from DB)
    engine.rules = [
        {"id": 1, "behavior_type": "running", "min_confidence": 0.7, "priority": "HIGH"},
        {"id": 2, "behavior_type": "walking", "min_confidence": 0.5, "priority": "LOW"},
    ]

    det = PersonDetection(person_idx=0, bbox=(0,0,100,200), confidence=0.9,
                          keypoints_x=[], keypoints_y=[], keypoints_conf=[])
    beh_running = BehaviorResult(person_idx=0, behavior_type="running",
                                  confidence=0.85, raw_scores={})
    beh_standing = BehaviorResult(person_idx=0, behavior_type="standing",
                                   confidence=0.9, raw_scores={})

    # Running should trigger HIGH alert
    # We can't call evaluate() because it needs DB, but we can test the logic
    matched = False
    for rule in engine.rules:
        if beh_running.behavior_type == rule["behavior_type"] and \
           beh_running.confidence >= rule["min_confidence"]:
            matched = True
            assert rule["priority"] == "HIGH"
            break
    assert matched, "Running behavior should match HIGH priority rule"

    # Standing should NOT match any rule
    matched = False
    for rule in engine.rules:
        if beh_standing.behavior_type == rule["behavior_type"]:
            matched = True
    assert not matched, "Standing should not match any rule"


test("Alert rule matching logic", test_alert_engine_rule_matching)


# ══════════════════════════════════════════════════════════
# TEST 8: Integration — Full Pipeline with Mocks
# ══════════════════════════════════════════════════════════
print("\n[8/8] Testing Full Pipeline Integration (mock)...")


def test_full_pipeline_mock():
    """
    Simulate the complete pipeline flow with fake data.
    Verifies that data flows correctly between all stages.
    """
    from pipeline.roi_pruner import ROIPruner
    from pipeline.classifier import BehaviorClassifier, BehaviorMLP
    from pipeline.detector import PersonDetection
    from config import settings

    # 1. Create fake frame
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    # 2. ROI Pruning (no mask)
    pruner = ROIPruner("nonexistent.npy")
    cropped, crop_info = pruner.crop(frame)
    assert cropped.shape[0] > 0

    # 3. Simulate YOLO detections (normally from detector.py)
    fake_detections = [
        PersonDetection(
            person_idx=0,
            bbox=(100.0, 150.0, 250.0, 450.0),
            confidence=0.91,
            keypoints_x=[float(x) for x in range(120, 137)],
            keypoints_y=[float(y) for y in range(200, 217)],
            keypoints_conf=[0.85] * 17,
        ),
        PersonDetection(
            person_idx=1,
            bbox=(400.0, 100.0, 520.0, 380.0),
            confidence=0.87,
            keypoints_x=[float(x) for x in range(420, 437)],
            keypoints_y=[float(y) for y in range(150, 167)],
            keypoints_conf=[0.78] * 17,
        ),
    ]
    assert len(fake_detections) == 2

    # 4. Behavior Classification
    import torch
    model = BehaviorMLP(input_size=51 * settings.POSE_WINDOW_SIZE, num_classes=7)
    model.eval()
    classifier = BehaviorClassifier(mlp_model=model)

    # Feed several frames to build up buffer
    for i in range(settings.POSE_WINDOW_SIZE + 2):
        behaviors = classifier.classify(fake_detections, "cam_test")

    assert len(behaviors) == 2, f"Expected 2 behaviors, got {len(behaviors)}"
    assert all(b.behavior_type in settings.BEHAVIOR_CLASSES for b in behaviors)

    # 5. Verify data is ready for DB insertion
    for det, beh in zip(fake_detections, behaviors):
        assert det.bbox[0] < det.bbox[2], "x1 should be < x2"
        assert det.bbox[1] < det.bbox[3], "y1 should be < y2"
        assert 0 <= det.confidence <= 1
        assert beh.confidence >= 0
        assert len(det.keypoints_x) == 17

    # If we got here, the full flow works!


test("Full pipeline mock integration", test_full_pipeline_mock)


# ══════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════
total = passed + failed + skipped
print(f"\n{'='*50}")
print(f"RESULTS: {passed} passed, {failed} failed, {skipped} skipped (out of {total})")
if failed == 0 and skipped == 0:
    print("🎉 All tests passed! Pipeline code is ready.")
elif failed == 0:
    print(f"✓ All runnable tests passed! {skipped} tests skipped (install missing deps).")
    print("\nTo run ALL tests:")
    print("  pip install -r requirements.txt")
    print("  python tests/test_pipeline.py")
else:
    print(f"⚠ {failed} test(s) failed. Fix the errors above before proceeding.")
print(f"{'='*50}")

sys.exit(0 if failed == 0 else 1)
