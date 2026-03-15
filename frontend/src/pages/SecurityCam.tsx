import { useState, useEffect } from 'react';
import CameraFilters from '../components/Security/CameraFilters';
import CameraFeed, { Camera } from '../components/Security/CameraFeed';
import AlertPanel from '../components/Security/AlertPanel';
import api from '../services/api';

export default function SecurityCam() {
  const [allCameras, setAllCameras] = useState<Camera[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<Camera>({} as Camera);
  const [filteredCameras, setFilteredCameras] = useState<Camera[]>([]);

  useEffect(() => {
    api.get('/cameras?include_inactive=false')
      .then(res => {
        const mapped: Camera[] = res.data.map((c: any, i: number) => ({
          id: String(c.camera_id),
          name: `Cam ${String.fromCharCode(65 + i)} - ${c.camera_name}`,
          location: c.location || c.camera_name,
          status: c.is_active ? 'active' : 'inactive',
          imageUrl: '',  // No live feed yet — pipeline will provide this
        }));
        setAllCameras(mapped);
        setFilteredCameras(mapped);
        if (mapped.length > 0) setSelectedCamera(mapped[0]);
      })
      .catch(() => {
        // Fallback to placeholder cameras if API fails
        const fallback: Camera[] = [
          { id: 'cam-1', name: 'Cam A - Entrance Lobby', location: 'Entrance Lobby', status: 'active', imageUrl: '' },
          { id: 'cam-2', name: 'Cam B - Parking Lot', location: 'Parking Lot', status: 'active', imageUrl: '' },
        ];
        setAllCameras(fallback);
        setFilteredCameras(fallback);
        setSelectedCamera(fallback[0]);
      })
      .finally(() => {});
  }, []);

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