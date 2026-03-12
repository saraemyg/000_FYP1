"""Behavior Classifier (TRANSFORM Stage 3) — MLP on pose keypoint sequences."""
import torch
import torch.nn as nn
import numpy as np
from collections import defaultdict, deque, Counter
from typing import List, Optional
from dataclasses import dataclass
from app.pipeline.detector import PersonDetection

BEHAVIOR_CLASSES = ["walking", "standing", "sitting", "running", "bending", "falling", "suspicious"]
POSE_WINDOW_SIZE = 15
SMOOTHING_WINDOW = 5


class BehaviorMLP(nn.Module):
    """Multi-Layer Perceptron for behavior classification."""
    def __init__(self, input_size: int, num_classes: int = 7, dropout: float = 0.3):
        super().__init__()
        self.input_size = input_size
        self.network = nn.Sequential(
            nn.Linear(input_size, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(256, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(128, 64), nn.ReLU(), nn.Dropout(dropout * 0.5),
            nn.Linear(64, num_classes),
        )

    def forward(self, x):
        return self.network(x)


@dataclass
class BehaviorResult:
    person_idx: int
    behavior_type: str
    confidence: float
    raw_scores: dict


class BehaviorClassifier:
    """Classifies behaviors using pose keypoint sequences + temporal smoothing."""

    def __init__(self, mlp_model: Optional[nn.Module]):
        self.model = mlp_model
        self.pose_buffers: dict = defaultdict(lambda: deque(maxlen=POSE_WINDOW_SIZE))
        self.prediction_history: dict = defaultdict(lambda: deque(maxlen=SMOOTHING_WINDOW))

    def classify(self, detections: List[PersonDetection], camera_id: str) -> List[BehaviorResult]:
        results = []
        for det in detections:
            key = f"{camera_id}_p{det.person_idx}"
            if det.keypoints_x and det.keypoints_y and det.keypoints_conf:
                kp = np.array([det.keypoints_x, det.keypoints_y, det.keypoints_conf]).T
                if det.bbox[2] > det.bbox[0] and det.bbox[3] > det.bbox[1]:
                    bw, bh = det.bbox[2] - det.bbox[0], det.bbox[3] - det.bbox[1]
                    kp[:, 0] = (kp[:, 0] - det.bbox[0]) / bw
                    kp[:, 1] = (kp[:, 1] - det.bbox[1]) / bh
                self.pose_buffers[key].append(kp.flatten())

            if self.model is not None and len(self.pose_buffers[key]) >= 3:
                result = self._predict(key, det.person_idx)
            else:
                result = BehaviorResult(person_idx=det.person_idx, behavior_type="unknown", confidence=0.0, raw_scores={})
            results.append(result)
        return results

    def _predict(self, person_key: str, person_idx: int) -> BehaviorResult:
        buf = list(self.pose_buffers[person_key])
        while len(buf) < POSE_WINDOW_SIZE:
            buf.append(buf[-1])
        buf = buf[-POSE_WINDOW_SIZE:]
        features = np.concatenate(buf).astype(np.float32)

        import torch as _torch
        device = "cuda" if _torch.cuda.is_available() else "cpu"
        with _torch.no_grad():
            x = _torch.tensor(features).unsqueeze(0).to(device)
            logits = self.model(x)
            probs = _torch.softmax(logits, dim=1).cpu().numpy()[0]

        pred_idx = int(np.argmax(probs))
        pred_label = BEHAVIOR_CLASSES[pred_idx]
        self.prediction_history[person_key].append(pred_label)
        if len(self.prediction_history[person_key]) >= 3:
            smoothed = Counter(self.prediction_history[person_key]).most_common(1)[0][0]
        else:
            smoothed = pred_label

        raw = {cls: float(probs[i]) for i, cls in enumerate(BEHAVIOR_CLASSES)}
        return BehaviorResult(person_idx=person_idx, behavior_type=smoothed, confidence=float(probs[pred_idx]), raw_scores=raw)
