# Complete Folder Structure

## Final Frontend Organization

```
frontend-prototype/
│
├── App.tsx                                    # Main app with routing (Login, SecurityCam, Alerts, Performance)
│
├── src/
│   │
│   ├── pages/                                 # All main pages
│   │   ├── Login.tsx                          # Authentication page
│   │   ├── SecurityCam.tsx                    # Live camera surveillance page
│   │   ├── AlertDashboard.tsx                 # Alert management and configuration page
│   │   └── PerformanceDashboard.tsx           # System performance monitoring page
│   │
│   └── components/                            # Organized by feature
│       │
│       ├── Auth/                              # Authentication components
│       │   ├── LoginForm.tsx                  # Form with username/password, validation
│       │   └── Logo.tsx                       # App logo and branding
│       │
│       ├── Security/                          # Security camera feed components
│       │   ├── NavigationBar.tsx              # Nav with Live Feed, Alerts, Performance tabs
│       │   ├── CameraFilters.tsx              # Search by location, camera, date, time
│       │   ├── CameraFeed.tsx                 # Main feed with detection boxes (WALK, STAND, RUN)
│       │   ├── CameraThumbnails.tsx           # 3 camera grid for quick switching
│       │   └── AlertPanel.tsx                 # Sidebar with summary + notifications
│       │
│       ├── Alert/                             # Alert dashboard components
│       │   ├── NavigationBar.tsx              # Nav with Live Feed, Alerts, Performance tabs
│       │   ├── AlertSummaryCards.tsx          # 4 cards: Total, High, Medium, Low priority
│       │   ├── BehaviorDistribution.tsx       # Donut chart with WALK/STAND/BEND/SIT %
│       │   ├── AlertPriorityChart.tsx         # Bar chart showing priority distribution
│       │   ├── AlertConfiguration.tsx         # Threshold sliders for each behavior
│       │   └── AlertHistory.tsx               # Table with filters, pagination, export
│       │
│       └── Performance/                       # Performance dashboard components
│           ├── NavigationBar.tsx              # Nav with Live Feed, Alerts, Performance tabs
│           ├── MetricsSummary.tsx             # 5 cards: Cameras, Frames, FPS, Time, Health
│           ├── PerformanceGraphs.tsx          # 3 charts: FPS, Detections, Resources
│           ├── PipelineStatus.tsx             # Processing components status (YOLO, MobileNet, ResNet)
│           └── ModelMetrics.tsx               # 3 tables with Precision, Recall, mAP
│
└── README.md                                  # Complete documentation
```

## Component Dependencies

### Pages
- **Login.tsx**: Uses `Auth/LoginForm.tsx`, `Auth/Logo.tsx`
- **SecurityCam.tsx**: Uses all `Security/*` components
- **AlertDashboard.tsx**: Uses all `Alert/*` components
- **PerformanceDashboard.tsx**: Uses all `Performance/*` components

### Navigation
- All authenticated pages use their respective `NavigationBar.tsx`
- Navigation bars are consistent in design but separate files for clean organization

## File Count Summary

```
Total Files: 22

Pages: 4
├── Login.tsx
├── SecurityCam.tsx
├── AlertDashboard.tsx
└── PerformanceDashboard.tsx

Components: 17
├── Auth (2)
│   ├── LoginForm.tsx
│   └── Logo.tsx
│
├── Security (5)
│   ├── NavigationBar.tsx
│   ├── CameraFilters.tsx
│   ├── CameraFeed.tsx
│   ├── CameraThumbnails.tsx
│   └── AlertPanel.tsx
│
├── Alert (6)
│   ├── NavigationBar.tsx
│   ├── AlertSummaryCards.tsx
│   ├── BehaviorDistribution.tsx
│   ├── AlertPriorityChart.tsx
│   ├── AlertConfiguration.tsx
│   └── AlertHistory.tsx
│
└── Performance (5)
    ├── NavigationBar.tsx
    ├── MetricsSummary.tsx
    ├── PerformanceGraphs.tsx
    ├── PipelineStatus.tsx
    └── ModelMetrics.tsx

Configuration: 2
├── App.tsx
└── README.md
```

## Design Alignment

### Based on Reference Images:

1. **Live_Viewingref.png** → SecurityCam.tsx
   - Left: Main camera feed with detection boxes
   - Right: Alert panel with summary and notifications
   - Bottom: Camera thumbnail grid
   - Top: Search and filter bar

2. **Alert_Dashboardref.png** → AlertDashboard.tsx
   - Top: 4 summary cards (Total, High, Medium, Low)
   - Middle: 2 charts (Behavior distribution, Priority distribution)
   - Middle: Alert configuration with sliders
   - Bottom: Alert history table with filters

3. **Performance_Metricsref.png** → PerformanceDashboard.tsx
   - Top: 5 metric cards (Cameras, Frames, FPS, Time, Health)
   - Middle: 3 performance graphs (FPS, Detections, Resources)
   - Bottom: Pipeline status + Model metrics

## Key Features Per Page

### Login
- Username/password authentication
- Password visibility toggle
- Remember me checkbox
- Forgot password link
- Error handling

### Security Camera
- Real-time detection overlay
- Multi-camera view
- Alert notifications
- Search and filtering
- Camera status indicators

### Alert Dashboard
- Priority-based organization
- Behavior distribution analysis
- Configurable thresholds
- Historical data table
- Export functionality

### Performance Dashboard
- Real-time metrics
- Resource monitoring
- Pipeline health
- Model accuracy tracking
- Compliance checking

## Color Coding

- **Blue**: Primary actions, navigation, info
- **Green**: Success, active status, low priority
- **Yellow**: Warnings, medium priority, caution
- **Red**: Errors, high priority, critical alerts
- **Purple**: Special features, attributes
- **Gray**: Backgrounds, disabled states, neutral

## Responsive Design

All components include:
- Grid layouts with responsive columns
- Mobile-friendly navigation
- Adaptive card sizing
- Flexible charts and tables
- Touch-friendly buttons

## Notes

- Components are self-contained with minimal dependencies
- Each feature folder contains related components only
- Navigation bars are duplicated for independence (can be unified later)
- All data is placeholder for demonstration
- Follows academic report specifications from Chapter 4 & 5
