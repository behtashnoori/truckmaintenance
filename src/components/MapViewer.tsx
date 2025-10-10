import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

const defaultIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

interface MapViewerProps {
  lat: number;
  lon: number;
  title?: string;
  height?: number;
}

export const MapViewer: React.FC<MapViewerProps> = ({ 
  lat, 
  lon, 
  title = "موقعیت ارائه‌دهنده",
  height = 300 
}) => {
  const position: [number, number] = [lat, lon];

  return (
    <div className="rounded-md overflow-hidden border">
      <MapContainer 
        center={position} 
        zoom={15} 
        style={{ height, width: '100%' }}
        scrollWheelZoom={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={position} icon={defaultIcon}>
          <Popup>
            <div className="text-center">
              <strong>{title}</strong>
              <br />
              <small>عرض: {lat.toFixed(6)}</small>
              <br />
              <small>طول: {lon.toFixed(6)}</small>
            </div>
          </Popup>
        </Marker>
      </MapContainer>
    </div>
  );
};
