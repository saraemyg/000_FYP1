import { useState } from 'react';
import NavigationBar from '../components/Security/NavigationBar';
import CameraFilters from '../components/Security/CameraFilters';
import CameraFeed, { Camera } from '../components/Security/CameraFeed';
import AlertPanel from '../components/Security/AlertPanel';

interface SecurityCamProps {
  onLogout: () => void;
}

export default function SecurityCam({ onLogout }: SecurityCamProps) {
  const allCameras: Camera[] = [
    {
      id: 'cam-1',
      name: 'Cam A - Parking Lot',
      location: 'Parking Lot',
      status: 'active',
      // ============================================
      // ADD YOUR CAMERA FEED URL HERE
      // Example: imageUrl: 'https://your-server.com/camera-feed/cam-1.jpg'
      // Or live stream: imageUrl: 'http://192.168.1.100:8080/video'
      // Leave empty ('') to show placeholder
      // ============================================
      imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTFcLhIRR7a2JQLVO83MRr4N3PO8JLKgjKLkA&s'
    },
    {
      id: 'cam-2',
      name: 'Cam B - Corridor A',
      location: 'Corridor A',
      status: 'active',
      // ============================================
      // ADD YOUR CAMERA FEED URL HERE
      // ============================================
      imageUrl: 'https://cdn.hashnode.com/res/hashnode/image/upload/v1693714471850/5fd2053d-8cb3-4483-b7da-61c3bf41400c.jpeg'
    },
    {
      id: 'cam-3',
      name: 'Cam C - Entrance Lobby',
      location: 'Entrance Lobby',
      status: 'active',
      // ============================================
      // ADD YOUR CAMERA FEED URL HERE
      // ============================================
      imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRFTVqGYFYZFKlRcOWLeHCrGXef8kZSZCXLZA&s'
    },
    {
      id: 'cam-4',
      name: 'Cam D - Building B',
      location: 'Building B',
      status: 'active',
      // ============================================
      // ADD YOUR CAMERA FEED URL HERE
      // ============================================
      imageUrl: 'https://viso.ai/wp-content/uploads/2023/01/smart-city-computer-vision-yolov7-deep-learning-1060x596.jpg'
    }
  ];

  const [selectedCamera, setSelectedCamera] = useState<Camera>(allCameras[0]);
  const [filteredCameras, setFilteredCameras] = useState<Camera[]>(allCameras);

  const handleFilterChange = (cameraName: string) => {
    if (cameraName === 'All Cameras') {
      setFilteredCameras(allCameras);
    } else {
      const filtered = allCameras.filter(cam => cam.name === cameraName);
      setFilteredCameras(filtered);
      if (filtered.length > 0) {
        setSelectedCamera(filtered[0]);
      }
    }
  };

  const handleViewCamera = (cameraId: string) => {
    const camera = allCameras.find(cam => cam.id === cameraId);
    if (camera) {
      setSelectedCamera(camera);
      // Scroll to top to show the camera feed
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <NavigationBar onLogout={onLogout} />
      
      <div className="max-w-[1920px] mx-auto p-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">Security Camera Feed</h1>
        
        <CameraFilters 
          cameras={allCameras} 
          onFilterChange={handleFilterChange}
        />
        
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mt-6">
          <div className="xl:col-span-2">
            <CameraFeed 
              cameras={filteredCameras}
              selectedCamera={selectedCamera}
              onSelectCamera={setSelectedCamera}
            />
          </div>
          
          <div className="xl:col-span-1">
            <AlertPanel onViewCamera={handleViewCamera} />
          </div>
        </div>
      </div>
    </div>
  );
}