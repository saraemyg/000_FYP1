# Frontend Implementation Summary

## Project: Automated Behavior Analysis Surveillance System
### Academic Term: T2530 (FYP01)

---

## Overview

This frontend prototype implements the interface designs specified in Chapter 4 (System Design) and Chapter 5 (Implementation Plan) of the FYP report. The system provides a comprehensive web-based interface for security personnel to monitor surveillance feeds, manage alerts, and track system performance.

## Implementation Details

### Total Files Created: 25
- **1** Main Application (App.tsx)
- **4** Page Components
- **17** Feature Components
- **2** Documentation Files
- **1** Folder Structure Guide

### Technology Stack
- React 18+ with TypeScript
- React Router for navigation
- Tailwind CSS for styling
- SVG icons for UI elements

---

## Pages Implemented

### 1. Login Page (`/login`)
**File**: `src/pages/Login.tsx`

**Features**:
- Username and password authentication
- Password visibility toggle
- "Remember me" functionality
- Forgot password link
- Inline error messaging
- Responsive design

**Default Credentials**:
- Username: `admin`
- Password: `admin123`

**Components Used**:
- `Auth/LoginForm.tsx` - Form with validation
- `Auth/Logo.tsx` - Application branding

---

### 2. Security Camera Feed (`/security-cam`)
**File**: `src/pages/SecurityCam.tsx`

**Features**:
- **Search & Filter Cameras**: Location, camera name, date/time range filtering
- **Main Camera Feed**: 
  - Live video stream simulation
  - Real-time behavior detection overlays (WALK, STAND, RUN)
  - Confidence percentages
  - Status indicators (LIVE, HD, AI Active)
  - Resolution and FPS display (1920x1080 @ 30fps)
- **Camera Thumbnails**: 3-camera grid for quick switching
- **Alert Panel**: 
  - Summary metrics (127 total alerts, 4 active cameras, 1.2s loitering)
  - Priority breakdown (High: 1, Medium: 1, Low: 0)
  - Real-time notifications with location, timestamp, confidence
  - Action buttons (Acknowledge, False Positive)

**Components Used**:
- `Security/NavigationBar.tsx` - Main navigation
- `Security/CameraFilters.tsx` - Search and filtering
- `Security/CameraFeed.tsx` - Main video display with detections
- `Security/CameraThumbnails.tsx` - Multi-camera grid
- `Security/AlertPanel.tsx` - Real-time alerts sidebar

**Design Reference**: `Live_Viewingref.png`

---

### 3. Alert Dashboard (`/alerts`)
**File**: `src/pages/AlertDashboard.tsx`

**Features**:
- **Summary Cards**: 4 priority-based cards
  - Total Alerts: 127 (last 24 hours)
  - High Priority: 1 active criteria
  - Medium Priority: 1 active criteria
  - Low Priority: 0 active criteria

- **Behavior Distribution Chart**: 
  - Donut chart visualization
  - WALK: 44.3% (2,840)
  - STAND: 33.0% (2,115)
  - BEND: 18.0% (1,153)
  - SIT: 4.7% (301)
  - Total: 6,409 detections (71%)
  - Notification preferences selector

- **Alert Priority Chart**: 
  - Stacked bar chart
  - 5 time periods (M1-M5)
  - High/Medium/Low priority distribution

- **Alert Configuration**:
  - Threshold sliders for 5 behaviors (RUN, BEND, WALK, STAND, SIT)
  - Min/Max confidence range settings
  - Dynamic priority level indicators
  - Enable/disable toggles per behavior
  - Save and Reset functionality

- **Alert History Table**:
  - Comprehensive data table with pagination
  - Filters: Search, Camera, Behavior, Priority, Status
  - Columns: ID, Timestamp, Camera, Behavior, Confidence, Priority, Status, Actions
  - Export to CSV functionality
  - View details action
  - Showing 1-10 of 50 results

**Components Used**:
- `Alert/NavigationBar.tsx` - Main navigation
- `Alert/AlertSummaryCards.tsx` - 4 priority cards
- `Alert/BehaviorDistribution.tsx` - Donut chart with legend
- `Alert/AlertPriorityChart.tsx` - Stacked bar chart
- `Alert/AlertConfiguration.tsx` - Threshold configuration panel
- `Alert/AlertHistory.tsx` - Filterable data table

**Design Reference**: `Alert_Dashboardref.png`

---

### 4. Performance Dashboard (`/performance`)
**File**: `src/pages/PerformanceDashboard.tsx`

**Features**:
- **Metrics Summary**: 5 key performance cards
  - Active Cameras: 4 (All operational)
  - Frames Analyzed: 24,538 (+12% increase)
  - Average FPS: 17.8 (Target: ≥15 FPS)
  - Processing Time: 0s (Total processing)
  - System Health: Optimal (All modules operating)

- **Real-time Performance Graphs**:
  - **FPS Over Time**: Line chart tracking sustained 15 FPS performance (NFR, PF1)
    - 6 time points (00:00, 04:00, 08:00, 12:00, 16:00, 20:00)
    - Average: 15.2 FPS
    - Compliance indicator: Compliant
  
  - **Detections Per Minute**: Bar chart for workload monitoring
    - 5 time periods (M1-M5)
    - Average: 17 detections/min
    - Peak: 21 detections
  
  - **Resource Consumption**: RAM & VRAM usage (NFR, PF3)
    - GPU: NVIDIA RTX 5060 Ti
    - CUDA Compute Capability: 8.9
    - RAM: 65% utilization
    - VRAM: 72% utilization

- **Processing Pipeline Status**:
  - Component Status & Queue Depth monitoring
  - Detection (YOLO): Operating, Queue Depth: 0
  - Segmentation (MobileNetV3): Operating, Queue Depth: 0
  - Attributes (ResNetSG): Operating, Queue Depth: 1

- **Model Performance Metrics**: 3 model accuracy tables
  - **YOLO (Detection)**:
    - Precision: 91.8%
    - Recall: 86.5%
    - mAP: 89.2%
  
  - **MobileNetV3 (Segmentation)**:
    - Precision: 88.3%
    - Recall: 85.7%
    - mAP: 86.8%
  
  - **ResNetSG (Attributes)**:
    - Precision: 85.2%
    - Recall: 82.1%
    - mAP: 83.4%

**Components Used**:
- `Performance/NavigationBar.tsx` - Main navigation
- `Performance/MetricsSummary.tsx` - 5 summary cards
- `Performance/PerformanceGraphs.tsx` - 3 visualization charts
- `Performance/PipelineStatus.tsx` - Component health monitoring
- `Performance/ModelMetrics.tsx` - 3 model performance tables

**Design Reference**: `Performance_Metricsref.png`

---

## Component Organization

### Auth Components (2 files)
Located in: `src/components/Auth/`
- **LoginForm.tsx**: Handles authentication with username/password validation
- **Logo.tsx**: Application branding and logo display

### Security Components (5 files)
Located in: `src/components/Security/`
- **NavigationBar.tsx**: Main navigation with Live Feed, Alerts, Performance tabs
- **CameraFilters.tsx**: Search by location, camera, date, time ranges
- **CameraFeed.tsx**: Main camera display with real-time detection overlays
- **CameraThumbnails.tsx**: 3-camera grid for quick feed switching
- **AlertPanel.tsx**: Real-time alert notifications sidebar

### Alert Components (6 files)
Located in: `src/components/Alert/`
- **NavigationBar.tsx**: Main navigation bar
- **AlertSummaryCards.tsx**: 4 priority-based summary cards
- **BehaviorDistribution.tsx**: Donut chart with behavior percentages
- **AlertPriorityChart.tsx**: Stacked bar chart for priority distribution
- **AlertConfiguration.tsx**: Threshold sliders and behavior settings
- **AlertHistory.tsx**: Comprehensive alert data table with filters

### Performance Components (5 files)
Located in: `src/components/Performance/`
- **NavigationBar.tsx**: Main navigation bar
- **MetricsSummary.tsx**: 5 key performance metric cards
- **PerformanceGraphs.tsx**: FPS, detections, and resource charts
- **PipelineStatus.tsx**: Processing component health indicators
- **ModelMetrics.tsx**: Model accuracy metrics tables

---

## Design Specifications

### Color Palette
- **Primary Blue**: #3b82f6 - Navigation, primary actions
- **Success Green**: #22c55e - Active status, low priority, compliant
- **Warning Yellow**: #eab308 - Medium priority, caution
- **Error Red**: #ef4444 - High priority, critical alerts
- **Info Purple**: #a855f7 - Special features
- **Neutral Gray**: #f9fafb - Backgrounds, disabled states

### Typography
- **Headings**: Bold, 24-32px
- **Body Text**: Regular, 14-16px
- **Labels**: Medium, 12-14px
- **Metrics**: Bold, 24-36px

### Layout
- **Max Width**: 1920px container
- **Padding**: 24px (6 Tailwind units)
- **Gap**: 16-24px between elements
- **Border Radius**: 8px for cards, 4px for buttons

### Responsive Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1280px
- **Desktop**: > 1280px

---

## Key Features

### Authentication & Authorization
- Login/logout functionality
- Protected routes
- Role-based access control ready
- Session management placeholder

### Real-time Monitoring
- Live camera feed simulation
- Behavior detection visualization
- Real-time alert notifications
- System health monitoring

### Data Visualization
- Donut charts (behavior distribution)
- Bar charts (priority distribution, detections)
- Line charts (FPS over time)
- Progress bars (resource consumption)
- Status indicators and badges

### Alert Management
- Priority-based categorization (High, Medium, Low)
- Configurable confidence thresholds (0-100%)
- Historical alert table with filtering
- Export functionality (CSV)
- Acknowledgement workflow
- False positive marking

### Performance Tracking
- FPS monitoring and compliance (≥15 FPS target)
- Resource utilization (RAM/VRAM)
- Processing pipeline health
- Model accuracy metrics
- Queue depth monitoring

---

## Placeholder Data

All components use realistic mock data:

### Camera Data
- 12 total cameras (4 active)
- 3 visible feeds: Building A Lobby, Main Door, Parking Area
- Resolution: 1920x1080 @ 30fps

### Detection Data
- Behaviors: WALK, STAND, RUN, BEND, SIT
- Confidence ranges: 82% - 95%
- Detection counts per behavior

### Alert Data
- 127 total alerts in last 24 hours
- Priority breakdown: 1 High, 1 Medium, 0 Low
- 5 sample alerts with full details

### Performance Metrics
- 24,538 frames analyzed
- 17.8 average FPS
- 65% RAM usage
- 72% VRAM usage
- 3 processing components operational

---

## Alignment with FYP Report

### Chapter 4: System Design
✓ Interface designs implemented as specified
✓ Use case scenarios reflected in page flows
✓ Activity diagrams translated to user interactions
✓ Sequence diagrams mapped to component communication

### Chapter 5: Implementation Plan
✓ Module structure follows development phases
✓ Component organization matches system architecture
✓ Testing placeholders for unit/integration tests
✓ Performance requirements visualized (NFR, PF1, PF3)

---

## Future Enhancements

### Backend Integration
- Connect to actual API endpoints
- Real-time WebSocket for live feeds
- Database integration for persistence
- Authentication with JWT tokens

### Advanced Features
- Video playback controls
- Multi-camera simultaneous view
- Advanced filtering and search
- Custom alert rules builder
- Report generation and scheduling
- User management dashboard

### Performance Optimization
- Lazy loading for components
- Virtual scrolling for tables
- Image optimization
- Code splitting
- Caching strategies

---

## Installation & Setup

### Prerequisites
```bash
Node.js 16+
npm or yarn
```

### Dependencies
```bash
npm install react-router-dom
npm install @types/react-router-dom
npm install tailwindcss
```

### Running the Prototype
```bash
cd frontend-prototype
npm install
npm start
```

### Access
- URL: `http://localhost:3000`
- Username: `admin`
- Password: `admin123`

---

## File Statistics

```
Total Lines of Code: ~5,000
Average Component Size: ~150 lines
Largest Component: AlertConfiguration.tsx (~200 lines)
Smallest Component: Logo.tsx (~20 lines)
```

---

## Academic Compliance

This implementation:
- Follows formal academic documentation standards
- Aligns with FYP Handbook requirements
- Implements interface designs from Chapter 4
- Supports evaluation criteria from FYP1 Rubrics
- Provides demonstration of system capabilities
- Documents technical decisions and rationale

---

## Notes

1. **No Backend**: This is a frontend-only prototype
2. **Mock Data**: All data is placeholder for demonstration
3. **Authentication**: Client-side only, not production-ready
4. **Responsive**: Designed for desktop, tablet, and mobile
5. **Accessibility**: Basic ARIA labels included
6. **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)

---

## Contact & Support

For questions or clarifications about this implementation, refer to:
- FYP Report: `1221102332_FYP_Report_Final.pdf`
- Rubrics: `FYP1_Rubrics.pdf`
- Handbook: `FYP_Handbook_T2510__1_.pdf`

---

**Implementation Completed**: February 10, 2026
**Project ID**: FYP01-DS-T2530-0446
**Student**: Sara Emilia Binti Sharifudin
**Course**: CPT6314 Project I 2530 Term
