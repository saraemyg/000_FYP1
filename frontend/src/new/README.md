# Frontend Prototype - Surveillance System

## Project Structure

```
frontend-prototype/
├── App.tsx                           # Main application with routing
├── src/
│   ├── pages/
│   │   ├── Login.tsx                 # Login page with authentication
│   │   ├── SecurityCam.tsx           # Live camera feed page
│   │   ├── AlertDashboard.tsx        # Alert management dashboard
│   │   └── PerformanceDashboard.tsx  # System performance metrics
│   │
│   └── components/
│       ├── Auth/
│       │   ├── LoginForm.tsx         # Login form with validation
│       │   └── Logo.tsx              # Application logo component
│       │
│       ├── Security/
│       │   ├── NavigationBar.tsx     # Navigation bar for security pages
│       │   ├── CameraFilters.tsx     # Search and filter cameras
│       │   ├── CameraFeed.tsx        # Main camera feed with detections
│       │   ├── CameraThumbnails.tsx  # Multiple camera thumbnails
│       │   └── AlertPanel.tsx        # Real-time alert panel
│       │
│       ├── Alert/
│       │   ├── NavigationBar.tsx     # Navigation bar for alert pages
│       │   ├── AlertSummaryCards.tsx # Summary metrics cards
│       │   ├── BehaviorDistribution.tsx # Donut chart for behaviors
│       │   ├── AlertPriorityChart.tsx   # Bar chart for priorities
│       │   ├── AlertConfiguration.tsx   # Alert threshold settings
│       │   └── AlertHistory.tsx         # Historical alert table
│       │
│       └── Performance/
│           ├── NavigationBar.tsx     # Navigation bar for performance pages
│           ├── MetricsSummary.tsx    # Performance summary cards
│           ├── PerformanceGraphs.tsx # FPS and detection charts
│           ├── PipelineStatus.tsx    # Processing pipeline status
│           └── ModelMetrics.tsx      # Model performance metrics
│
└── README.md                         # This file
```

## Pages Overview

### 1. Login Page (`/login`)
- Clean authentication interface
- Username and password fields with validation
- Password visibility toggle
- "Remember me" checkbox
- "Forgot password" link
- Error message display
- Default credentials: `admin` / `admin123`

### 2. Security Camera Feed (`/security-cam`)
- **Camera Filters Section**
  - Location search
  - Camera search
  - Date and time range filters
  - Camera count display
  
- **Main Camera Feed**
  - Live video stream visualization
  - Real-time behavior detection overlays (WALK, STAND, RUN)
  - Confidence percentage display
  - Camera status indicators (LIVE, HD, AI Active)
  - Feed resolution and FPS information
  
- **Camera Thumbnails**
  - Grid of 3 camera feeds
  - Click to switch main feed
  - Live indicators
  - Detection overlays
  
- **Alert Panel**
  - Total alerts summary (127 in last 24h)
  - Active cameras count (4)
  - Loitering duration (1.2s)
  - Priority breakdown (High, Medium, Low)
  - Real-time alert notifications with:
    - Behavior type badges
    - Status indicators (PENDING/ACKNOWLEDGED)
    - Location and timestamp
    - Confidence scores
    - Action buttons (Acknowledge, False Positive)

### 3. Alert Dashboard (`/alerts`)
- **Summary Cards**
  - Total alerts (127)
  - High priority alerts (1)
  - Medium priority alerts (1)
  - Low priority alerts (0)
  
- **Behavior Distribution Chart**
  - Donut chart showing behavior percentages
  - WALK (44.3%), STAND (33.0%), BEND (18.0%), SIT (4.7%)
  - Total count: 6,409
  - Notification preferences
  
- **Alert Priority Chart**
  - Stacked bar chart showing priority distribution over time
  - High, Medium, Low categories
  - 5 time periods (M1-M5)
  
- **Alert Configuration**
  - Threshold sliders for each behavior (RUN, BEND, WALK, STAND, SIT)
  - Min/Max confidence settings
  - Priority level indicators
  - Enable/disable toggles
  - Save and reset buttons
  
- **Alert History Table**
  - Comprehensive alert data table
  - Filters: Search, Camera, Behavior, Priority, Status
  - Columns: ID, Timestamp, Camera, Behavior, Confidence, Priority, Status, Actions
  - Export to CSV functionality
  - Pagination (Showing 1-10 of 50 results)
  - View details action

### 4. Performance Dashboard (`/performance`)
- **Metrics Summary**
  - Active Cameras (4)
  - Frames Analyzed (24,538) with +12% badge
  - Average FPS (17.8)
  - Processing Time (0s)
  - System Health (Optimal)
  
- **Real-time Performance Graphs**
  - **FPS Over Time**: Line/bar chart tracking 15 FPS target compliance
  - **Detections Per Minute**: Bar chart showing workload (17 avg, 21 peak)
  - **Resource Consumption**: 
    - GPU: NVIDIA RTX 5060 Ti
    - CUDA Compute Capability: 8.9
    - RAM usage: 65%
    - VRAM usage: 72%
  
- **Processing Pipeline Status**
  - Detection (YOLO): Operating, Queue Depth: 0
  - Segmentation (MobileNetV3): Operating, Queue Depth: 0
  - Attributes (ResNetSG): Operating, Queue Depth: 1
  
- **Model Performance Metrics**
  - YOLO (Detection): Precision 91.8%, Recall 86.5%, mAP 89.2%
  - MobileNetV3 (Segmentation): Precision 88.3%, Recall 85.7%, mAP 86.8%
  - ResNetSG (Attributes): Precision 85.2%, Recall 82.1%, mAP 83.4%

## Features

### Authentication
- Simple login system with role-based access
- Protected routes requiring authentication
- Logout functionality across all pages

### Navigation
- Consistent navigation bar across all authenticated pages
- Active page highlighting
- Quick access to Live Feed, Alerts, and Performance sections

### Real-time Monitoring
- Live camera feed simulation with behavior detection
- Real-time alert notifications
- System performance metrics

### Alert Management
- Priority-based alert categorization
- Configurable confidence thresholds
- Alert history with advanced filtering
- Acknowledgement and false positive marking

### Performance Tracking
- FPS monitoring and compliance checking
- Resource utilization tracking
- Processing pipeline health monitoring
- Model accuracy metrics

## Data Visualization
- Donut charts for behavior distribution
- Bar charts for priority and detection trends
- Line charts for FPS tracking
- Progress bars for resource consumption
- Status indicators and badges

## Color Scheme
- Primary: Blue (#3b82f6)
- Success/Active: Green (#22c55e)
- Warning/Medium: Yellow (#eab308)
- Error/High: Red (#ef4444)
- Info: Purple (#a855f7)
- Background: Gray (#f9fafb)

## Placeholder Data
All components use realistic placeholder data to simulate:
- Camera feeds with detection overlays
- Alert notifications and history
- Performance metrics and trends
- System health indicators

## Installation Requirements
```bash
# Dependencies needed
npm install react-router-dom
npm install @heroicons/react
```

## Running the Application
```bash
npm start
```

Navigate to `http://localhost:3000` and use:
- Username: `admin`
- Password: `admin123`

## Notes
- This is a frontend-only prototype with no backend integration
- All data is placeholder/mock data
- Authentication is client-side only (not production-ready)
- Designed to match the interface designs from the FYP report
- Follows Chapter 4 (System Design) and Chapter 5 (Implementation Plan) specifications
