"""
Behavior Classifier (TRANSFORM Stage 3)
=========================================
Classifies detected persons' behaviors using pose keypoints + temporal features.

How it works:
1. Receives 17 keypoints for a detected person
2. Stores keypoints in a rolling buffer (sliding window of recent frames)
3. When buffer has enough frames, flattens into a feature vector
4. Feeds into trained MLP → outputs behavior label + confidence
5. Applies temporal smoothing (majority vote) to reduce flickering

The MLP model is trained separately in a Jupyter notebook (Step 3).
This file also defines the MLP architecture class so model_loader can reconstruct it.
"""

import torch
import torch.nn as nn
import numpy as np
import logging
from collections import defaultdict, deque
from typing import List, Optional, Tuple
from dataclasses import dataclass

from config import settings
from pipeline.detector import PersonDetection

logger = logging.getLogger(__name__)


# ── MLP Architecture ─────────────────────────────────────
# This MUST match what's used in the training notebook

class BehaviorMLP(nn.Module):
    """
    Multi-Layer Perceptron for behavior classification.
    
    Input: Flattened pose features (17 keypoints × 3 values × N frames)
    Output: Probability distribution over behavior classes
    
    Architecture is intentionally simple — your report says MLP with 0.5-1M params.
    """

    def __init__(self, input_size: int, num_classes: int = 7, dropout: float = 0.3):
        super().__init__()
        self.input_size = input_size
        self.network = nn.Sequential(
            nn.Linear(input_size, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(dropout),

            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(dropout),

            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(dropout * 0.5),

            nn.Linear(64, num_classes),
        )

    def forward(self, x):
        return self.network(x)


# ── Behavior Classifier (Runtime) ────────────────────────

@dataclass
class BehaviorResult:
    """Classification result for one person."""
    person_idx: int
    behavior_type: str         # predicted label
    confidence: float          # softmax confidence
    raw_scores: dict           # {class_name: probability} for all classes


class BehaviorClassifier:
    """
    Classifies behaviors using pose keypoint sequences.
    
    Maintains per-person buffers to capture temporal motion patterns.
    
    Usage:
        classifier = BehaviorClassifier(mlp_model)
        results = classifier.classify(detections, camera_id="cam_01")
    """

    def __init__(self, mlp_model: Optional[nn.Module]):
        self.model = mlp_model
        self.classes = settings.BEHAVIOR_CLASSES
        self.window_size = settings.POSE_WINDOW_SIZE
        self.smoothing_window = settings.TEMPORAL_SMOOTHING_WINDOW

        # Per-person keypoint buffers: {camera_person_key: deque of keypoint arrays}
        self.pose_buffers: dict = defaultdict(lambda: deque(maxlen=self.window_size))

        # Per-person prediction history for temporal smoothing
        self.prediction_history: dict = defaultdict(lambda: deque(maxlen=self.smoothing_window))

    def classify(self, detections: List[PersonDetection], camera_id: str) -> List[BehaviorResult]:
        """
        Classify behavior for each detected person.
        
        Args:
            detections: List of PersonDetection from detector
            camera_id: Camera identifier (for per-person tracking across frames)
        
        Returns:
            List of BehaviorResult, one per detection
        """
        results = []

        for det in detections:
            # Create a unique key for this person (simple: camera + person index)
            # In production you'd use a proper tracker (DeepSORT, ByteTrack)
            person_key = f"{camera_id}_p{det.person_idx}"

            # Add current keypoints to this person's buffer
            if det.keypoints_x and det.keypoints_y and det.keypoints_conf:
                kp_array = self._keypoints_to_array(det)
                self.pose_buffers[person_key].append(kp_array)

            # Classify if we have enough history and model is loaded
            if self.model is not None and len(self.pose_buffers[person_key]) >= 3:
                result = self._predict(person_key, det.person_idx)
            else:
                # Not enough data yet or no model — return "unknown"
                result = BehaviorResult(
                    person_idx=det.person_idx,
                    behavior_type="unknown",
                    confidence=0.0,
                    raw_scores={},
                )

            results.append(result)

        return results

    def _keypoints_to_array(self, det: PersonDetection) -> np.ndarray:
        """Convert keypoints to normalized feature array."""
        # Stack into (17, 3) array: [x, y, confidence] per keypoint
        kp = np.array([det.keypoints_x, det.keypoints_y, det.keypoints_conf]).T  # (17, 3)

        # Normalize x,y relative to bounding box (makes features position-invariant)
        if det.bbox[2] > det.bbox[0] and det.bbox[3] > det.bbox[1]:
            bbox_w = det.bbox[2] - det.bbox[0]
            bbox_h = det.bbox[3] - det.bbox[1]
            kp[:, 0] = (kp[:, 0] - det.bbox[0]) / bbox_w  # x normalized to [0,1]
            kp[:, 1] = (kp[:, 1] - det.bbox[1]) / bbox_h  # y normalized to [0,1]

        return kp.flatten()  # (51,) = 17 * 3

    def _predict(self, person_key: str, person_idx: int) -> BehaviorResult:
        """Run MLP inference on buffered pose sequence."""
        buffer = list(self.pose_buffers[person_key])

        # Pad buffer to window_size if needed (repeat last frame)
        while len(buffer) < self.window_size:
            buffer.append(buffer[-1])

        # Take the most recent window_size frames
        buffer = buffer[-self.window_size:]

        # Flatten: (window_size, 51) → (window_size * 51,)
        features = np.concatenate(buffer).astype(np.float32)

        # Run inference
        with torch.no_grad():
            x = torch.tensor(features).unsqueeze(0).to(settings.DEVICE)  # (1, input_size)
            logits = self.model(x)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]

        # Get top prediction
        pred_idx = int(np.argmax(probs))
        pred_label = self.classes[pred_idx]
        pred_conf = float(probs[pred_idx])

        # Temporal smoothing: majority vote over recent predictions
        self.prediction_history[person_key].append(pred_label)
        if len(self.prediction_history[person_key]) >= 3:
            from collections import Counter
            counts = Counter(self.prediction_history[person_key])
            smoothed_label = counts.most_common(1)[0][0]
        else:
            smoothed_label = pred_label

        # Build raw scores dict
        raw_scores = {cls: float(probs[i]) for i, cls in enumerate(self.classes)}

        return BehaviorResult(
            person_idx=person_idx,
            behavior_type=smoothed_label,
            confidence=pred_conf,
            raw_scores=raw_scores,
        )
