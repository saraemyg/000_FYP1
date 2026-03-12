"""
Pipeline Test — verifies all components work without GPU, DB, or real videos.
Run: cd backend && python -m tests.test_pipeline
"""
import sys, os
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

passed = failed = skipped = 0

def test(name, func):
    global passed, failed, skipped
    try:
        func()
        print(f"  ✓ {name}")
        passed += 1
    except ImportError as e:
        mod = str(e).split("'")[1] if "'" in str(e) else str(e)
        print(f"  ⊘ {name} [SKIP — pip install {mod}]")
        skipped += 1
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        failed += 1

# ── 1. Extractor ──
print("\n[1] Extractor...")
def t_extractor():
    from app.pipeline.extractor import FrameExtractor, FrameData
    ext = FrameExtractor("cam_test", "fake.mp4", target_fps=15)
    assert ext.camera_id == "cam_test"
    fd = FrameData(frame=np.zeros((480, 640, 3), dtype=np.uint8), frame_number=1, timestamp=datetime.utcnow(), camera_id="cam_01")
    assert fd.frame.shape == (480, 640, 3)
test("FrameExtractor + FrameData", t_extractor)

# ── 2. ROI Pruner ──
print("\n[2] ROI Pruner...")
def t_pruner_no_mask():
    from app.pipeline.roi_pruner import ROIPruner
    p = ROIPruner("nonexistent.npy")
    f = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    cropped, info = p.crop(f)
    assert cropped.shape == f.shape
    assert info.area_reduction == 0.0
test("No mask → full frame passthrough", t_pruner_no_mask)

def t_pruner_with_mask():
    import tempfile
    from app.pipeline.roi_pruner import ROIPruner
    mask = np.zeros((480, 640), dtype=np.uint8)
    mask[100:300, 150:500] = 1
    tmp = os.path.join(tempfile.gettempdir(), "_test_mask.npy")
    np.save(tmp, mask)
    p = ROIPruner(tmp)
    f = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    cropped, info = p.crop(f)
    assert cropped.shape[0] < f.shape[0] or cropped.shape[1] < f.shape[1]
    assert info.area_reduction > 0
    os.remove(tmp)
test("Mask → smaller cropped frame", t_pruner_with_mask)

def t_coord_map():
    from app.pipeline.roi_pruner import ROIPruner, CropInfo
    ci = CropInfo(x1=100, y1=50, x2=500, y2=400, original_w=640, original_h=480, area_reduction=35.0)
    result = ROIPruner.map_bbox_to_original((10, 20, 110, 220), ci)
    assert result == (110, 70, 210, 270), f"Got {result}"
test("Coordinate remapping", t_coord_map)

# ── 3. Detector data ──
print("\n[3] Detector...")
def t_detection_struct():
    from app.pipeline.detector import PersonDetection
    d = PersonDetection(person_idx=0, bbox=(100.0, 200.0, 300.0, 500.0), confidence=0.92,
                        keypoints_x=[float(i) for i in range(17)],
                        keypoints_y=[float(i+100) for i in range(17)],
                        keypoints_conf=[0.9]*17)
    assert len(d.keypoints_x) == 17
test("PersonDetection struct", t_detection_struct)

# ── 4. Classifier ──
print("\n[4] Classifier...")
def t_mlp_arch():
    import torch
    from app.pipeline.classifier import BehaviorMLP
    m = BehaviorMLP(input_size=51*15, num_classes=7)
    out = m(torch.randn(2, 51*15))
    assert out.shape == (2, 7)
test("MLP forward pass", t_mlp_arch)

def t_classify_no_model():
    from app.pipeline.classifier import BehaviorClassifier
    from app.pipeline.detector import PersonDetection
    c = BehaviorClassifier(mlp_model=None)
    d = PersonDetection(person_idx=0, bbox=(0,0,100,200), confidence=0.9,
                        keypoints_x=[0.0]*17, keypoints_y=[0.0]*17, keypoints_conf=[0.9]*17)
    r = c.classify([d], "cam_test")
    assert r[0].behavior_type == "unknown"
test("Classify without model → unknown", t_classify_no_model)

def t_classify_with_model():
    import torch
    from app.pipeline.classifier import BehaviorClassifier, BehaviorMLP, BEHAVIOR_CLASSES, POSE_WINDOW_SIZE
    from app.pipeline.detector import PersonDetection
    m = BehaviorMLP(input_size=51*POSE_WINDOW_SIZE, num_classes=7)
    m.eval()
    c = BehaviorClassifier(mlp_model=m)
    for i in range(POSE_WINDOW_SIZE + 1):
        d = PersonDetection(person_idx=0, bbox=(10,20,110,320), confidence=0.9,
                            keypoints_x=[float(j+i) for j in range(17)],
                            keypoints_y=[float(j+100+i) for j in range(17)],
                            keypoints_conf=[0.8]*17)
        r = c.classify([d], "cam_test")
    assert r[0].behavior_type in BEHAVIOR_CLASSES
    assert r[0].confidence > 0
test("Classify with mock model → valid label", t_classify_with_model)

# ── 5. Models ──
print("\n[5] DB Models...")
def t_new_models():
    from app.models.behavior import Behavior
    from app.models.pose_keypoint import PoseKeypoint
    assert Behavior.__tablename__ == "behaviors"
    assert PoseKeypoint.__tablename__ == "pose_keypoints"
test("Behavior + PoseKeypoint models", t_new_models)

def t_models_init():
    from app.models import Behavior, PoseKeypoint, User, Detection, Camera, AlertRule
    assert Behavior is not None
    assert PoseKeypoint is not None
test("All models importable from __init__", t_models_init)

# ── 6. Integration ──
print("\n[6] Integration...")
def t_full_flow():
    import torch
    from app.pipeline.roi_pruner import ROIPruner
    from app.pipeline.classifier import BehaviorClassifier, BehaviorMLP, BEHAVIOR_CLASSES, POSE_WINDOW_SIZE
    from app.pipeline.detector import PersonDetection
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    pruner = ROIPruner("nope.npy")
    cropped, ci = pruner.crop(frame)
    dets = [PersonDetection(person_idx=0, bbox=(100,150,250,450), confidence=0.91,
                            keypoints_x=[float(x) for x in range(120,137)],
                            keypoints_y=[float(y) for y in range(200,217)],
                            keypoints_conf=[0.85]*17)]
    m = BehaviorMLP(input_size=51*POSE_WINDOW_SIZE, num_classes=7); m.eval()
    c = BehaviorClassifier(mlp_model=m)
    for i in range(POSE_WINDOW_SIZE + 2):
        behs = c.classify(dets, "cam_test")
    assert behs[0].behavior_type in BEHAVIOR_CLASSES
test("Full E→T mock flow", t_full_flow)

# ── Summary ──
total = passed + failed + skipped
print(f"\n{'='*50}")
print(f"RESULTS: {passed} passed, {failed} failed, {skipped} skipped (of {total})")
if failed == 0:
    print("🎉 All runnable tests passed!" + (f" ({skipped} need deps)" if skipped else ""))
else:
    print(f"⚠ {failed} test(s) failed — fix before proceeding")
print(f"{'='*50}")
sys.exit(0 if failed == 0 else 1)
