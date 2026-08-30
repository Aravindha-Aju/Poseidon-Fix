import React, { useState, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import * as turf from '@turf/turf';
import { api } from './services/api';

import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
L.Marker.prototype.options.icon = L.icon({ iconUrl: icon, shadowUrl: iconShadow, iconSize: [25, 41], iconAnchor: [12, 41] });

const createNormalShipIcon = () => L.divIcon({ className: 'normal-ship', html: `<div style="background-color: #3b82f6; width: 10px; height: 10px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.5);"></div>`, iconSize: [14, 14], iconAnchor: [7, 7] });
const createDarkShipIcon = () => L.divIcon({ className: 'dark-ship', html: `<div style="background-color: #ef4444; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 10px #ef4444; animation: pulse-red 1.5s infinite;"></div>`, iconSize: [16, 16], iconAnchor: [8, 8] });
const createSanctuaryIcon = (isThreatened) => L.divIcon({ className: 'sanctuary-marker', html: `<div style="background-color: ${isThreatened ? '#ef4444' : '#10b981'}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 8px ${isThreatened ? '#ef4444' : '#10b981'}; ${isThreatened ? 'animation: pulse-red 1s infinite;' : ''}"></div>`, iconSize: [18, 18], iconAnchor: [9, 9] });

const ECOLOGICAL_ZONES = [
  { name: "Lakshadweep Marine Sanctuary", lat: 10.5, lng: 72.6, type: "Coral Reefs", region: "Arabian Sea" },
  { name: "Gulf of Mannar Biosphere Reserve", lat: 9.15, lng: 79.15, type: "Coral Reefs + Mangroves", region: "Bay of Bengal" },
  { name: "Sundarbans National Park", lat: 21.95, lng: 89.0, type: "Mangroves (Tiger Reserve)", region: "Bay of Bengal" }
];

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [pipelineData, setPipelineData] = useState(null);
  const [showEvidenceModal, setShowEvidenceModal] = useState(false);
  const [threatenedZones, setThreatenedZones] = useState([]);
  const mapRef = useRef();

  const runInvestigation = async () => {
    setIsLoading(true);
    try {
      const data = await api.runPipeline("demo_case_001", "sample_sar_001", 12);
      setPipelineData(data);
      if (data.impact && data.impact.threatened_zones) setThreatenedZones(data.impact.threatened_zones.map(z => z.name));
    } catch (error) {
      console.error("Pipeline failed:", error);
      alert("Investigation failed. Check backend console.");
    } finally {
      setIsLoading(false);
    }
  };

  const generateHash = () => pipelineData && pipelineData.evidence ? pipelineData.evidence.sha256_hash : 'SHA-256: N/A';
  const downloadEvidenceJSON = () => {
    if (!pipelineData) return;
    const blob = new Blob([JSON.stringify(pipelineData.evidence, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = `evidence_${pipelineData.case_id}.json`;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
  };

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', fontFamily: 'Inter, sans-serif', backgroundColor: '#0f172a', color: '#e2e8f0' }}>
      {threatenedZones.length > 0 && (
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', backgroundColor: '#ef4444', color: 'white', padding: '10px', textAlign: 'center', fontWeight: 'bold', zIndex: 1500, fontSize: '14px' }}>
          ECOLOGICAL EMERGENCY: Oil slick threatens {threatenedZones.join(' & ')}. DEPLOY CONTAINMENT BOOMS IMMEDIATELY.
        </div>
      )}

      <MapContainer ref={mapRef} center={[12.0, 78.0]} zoom={5} style={{ width: '100%', height: '100%' }} worldCopyJump={false} maxBounds={[[-90, -180], [90, 180]]} maxBoundsViscosity={1.0}>
        <TileLayer attribution='&copy; OpenStreetMap' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" noWrap={true} />
        
        {ECOLOGICAL_ZONES.map((zone, idx) => {
          const protectionZone = turf.circle([zone.lng, zone.lat], 150, { units: 'kilometers', steps: 32 });
          return (
            <GeoJSON key={`zone-${idx}`} data={protectionZone} style={{ color: threatenedZones.includes(zone.name) ? '#ef4444' : '#10b981', weight: 2, fillColor: threatenedZones.includes(zone.name) ? '#fecaca' : '#d1fae5', fillOpacity: 0.2, dashArray: '8, 4' }}>
              <Popup><b>{zone.name}</b><br/>Type: {zone.type}<br/>Protected Radius: 150km<br/>{threatenedZones.includes(zone.name) && <span style={{color: 'red', fontWeight: 'bold'}}>UNDER THREAT</span>}</Popup>
            </GeoJSON>
          );
        })}
        {ECOLOGICAL_ZONES.map((zone, idx) => (
          <Marker key={idx} position={[zone.lat, zone.lng]} icon={createSanctuaryIcon(threatenedZones.includes(zone.name))}>
            <Popup><b>{zone.name}</b><br/>Type: {zone.type}<br/>Region: {zone.region}</Popup>
          </Marker>
        ))}

        {pipelineData && pipelineData.detection && pipelineData.detection.spill_polygon && (
          <GeoJSON data={pipelineData.detection.spill_polygon} style={{ color: '#b91c1c', weight: 2, fillColor: '#7f1d1d', fillOpacity: 0.6 }}>
            <Popup><b>Detected Oil Spill</b><br/>Confidence: {(pipelineData.detection.confidence * 100).toFixed(1)}%<br/>Data Origin: INFERRED (U-Net)</Popup>
          </GeoJSON>
        )}
        {pipelineData && pipelineData.drift && pipelineData.drift.drift_path && (
          <Polyline positions={pipelineData.drift.drift_path.coordinates.map(c => [c[1], c[0]])} pathOptions={{ color: '#f59e0b', weight: 3, opacity: 0.8, dashArray: '5, 5' }} />
        )}
        {pipelineData && pipelineData.source_zone && (
          <GeoJSON data={{type: "Polygon", coordinates: [[[pipelineData.source_zone.centroid[0] - 0.05, pipelineData.source_zone.centroid[1] - 0.05], [pipelineData.source_zone.centroid[0] + 0.05, pipelineData.source_zone.centroid[1] - 0.05], [pipelineData.source_zone.centroid[0] + 0.05, pipelineData.source_zone.centroid[1] + 0.05], [pipelineData.source_zone.centroid[0] - 0.05, pipelineData.source_zone.centroid[1] + 0.05], [pipelineData.source_zone.centroid[0] - 0.05, pipelineData.source_zone.centroid[1] - 0.05]]]}} style={{ color: '#8b5cf6', weight: 2, fillColor: '#8b5cf6', fillOpacity: 0.2, dashArray: '4, 4' }}>
            <Popup><b>Estimated Source Zone</b><br/>Uncertainty: {pipelineData.source_zone.uncertainty_km} km<br/>Confidence: {(pipelineData.source_zone.confidence_level * 100).toFixed(0)}%</Popup>
          </GeoJSON>
        )}
        {pipelineData && pipelineData.vessels && pipelineData.vessels.map(ship => {
          const behavior = pipelineData.behavior[ship.mmsi] || {};
          const isDark = behavior.is_dark_vessel || false;
          const traj = ship.trajectory || [];
          const lastPoint = traj.length > 0 ? traj[traj.length - 1] : null;
          if (!lastPoint) return null;
          return (
            <Marker key={ship.mmsi} position={[lastPoint.lat, lastPoint.lon]} icon={isDark ? createDarkShipIcon() : createNormalShipIcon()}>
              <Popup><b>{ship.name}</b><br/>MMSI: {ship.mmsi}<br/>Type: {ship.type}<br/>Status: {isDark ? 'DARK VESSEL (AIS GAP)' : 'NORMAL'}</Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {showEvidenceModal && (
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100vw', height: '100vh', backgroundColor: 'rgba(0,0,0,0.7)', zIndex: 2000, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <div style={{ backgroundColor: '#1e293b', padding: '24px', borderRadius: '8px', border: '1px solid #334155', width: '500px', maxWidth: '90%' }}>
            <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', color: '#f8fafc', fontWeight: 'bold', display: 'flex', justifyContent: 'space-between' }}>IMMUTABLE EVIDENCE LOCKER <button onClick={() => setShowEvidenceModal(false)} style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '20px', cursor: 'pointer' }}>x</button></h3>
            <div style={{ backgroundColor: '#0f172a', padding: '16px', borderRadius: '6px', border: '1px solid #334155', marginBottom: '16px' }}>
              <div style={{ fontSize: '12px', color: '#10b981', marginBottom: '8px', fontWeight: 'bold' }}>[ SEALED ] Evidence Package</div>
              <div style={{ fontSize: '11px', color: '#94a3b8', fontFamily: 'monospace', wordBreak: 'break-all' }}>{generateHash()}</div>
            </div>
            <div style={{ fontSize: '12px', color: '#cbd5e1', lineHeight: '1.6' }}>
              <div><strong>Case ID:</strong> {pipelineData?.case_id}</div>
              <div><strong>Top Candidate:</strong> {pipelineData?.attribution?.top_candidate?.name}</div>
              <div><strong>Threat Level:</strong> {pipelineData?.impact?.overall_threat_level}</div>
              <button onClick={downloadEvidenceJSON} style={{ marginTop: '16px', width: '100%', padding: '10px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer' }}>DOWNLOAD EVIDENCE JSON</button>
            </div>
          </div>
        </div>
      )}

      <div style={{ position: 'absolute', top: threatenedZones.length > 0 ? '50px' : '20px', left: '20px', backgroundColor: 'rgba(15, 23, 42, 0.95)', padding: '20px', borderRadius: '8px', border: '1px solid #334155', width: '320px', zIndex: 1000 }}>
        <h1 style={{ margin: '0 0 5px 0', fontSize: '20px', color: '#f8fafc', fontWeight: '800' }}>POSEIDON</h1>
        <p style={{ margin: '0 0 20px 0', fontSize: '10px', color: '#94a3b8', textTransform: 'uppercase' }}>Maritime Forensics Command Center</p>
        {!pipelineData ? (
          <button onClick={runInvestigation} disabled={isLoading} style={{ width: '100%', padding: '12px', backgroundColor: isLoading ? '#475569' : '#3b82f6', color: 'white', border: 'none', borderRadius: '4px', fontWeight: 'bold', cursor: isLoading ? 'not-allowed' : 'pointer', fontSize: '14px' }}>
            {isLoading ? 'RUNNING INVESTIGATION...' : 'RUN INVESTIGATION (CASE 001)'}
          </button>
        ) : (
          <div>
            <div style={{ marginBottom: '15px', padding: '10px', backgroundColor: '#1e293b', borderRadius: '4px', border: '1px solid #334155' }}>
              <div style={{ fontSize: '11px', color: '#94a3b8', marginBottom: '4px' }}>INVESTIGATION COMPLETE</div>
              <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#f8fafc' }}>Case: {pipelineData.case_id}</div>
            </div>
            <button onClick={() => setPipelineData(null)} style={{ width: '100%', padding: '8px', backgroundColor: '#475569', color: 'white', border: 'none', borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer' }}>RESET</button>
          </div>
        )}
      </div>

      <div style={{ position: 'absolute', top: threatenedZones.length > 0 ? '50px' : '20px', right: '20px', width: '350px', zIndex: 1000, display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '90vh' }}>
        <div style={{ backgroundColor: 'rgba(15, 23, 42, 0.95)', padding: '15px', borderRadius: '8px', border: '1px solid #334155' }}>
          <h3 style={{ margin: '0 0 10px 0', fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase', borderBottom: '1px solid #334155', paddingBottom: '5px' }}>Global Situational Awareness</h3>
          <div style={{ fontSize: '12px', lineHeight: '1.6' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Vessels Analyzed:</span><span>{pipelineData ? pipelineData.vessels.length : 0}</span></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Active Incidents:</span><span style={{ color: pipelineData ? '#f59e0b' : '#64748b' }}>{pipelineData ? 1 : 0}</span></div>
          </div>
        </div>
        <div style={{ backgroundColor: 'rgba(15, 23, 42, 0.95)', padding: '15px', borderRadius: '8px', border: '1px solid #334155', flex: 1, overflowY: 'auto' }}>
          <h3 style={{ margin: '0 0 10px 0', fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase', borderBottom: '1px solid #334155', paddingBottom: '5px' }}>Attribution Ranking</h3>
          {!pipelineData ? (
            <p style={{ fontSize: '11px', color: '#64748b' }}>Run investigation to see candidate ranking.</p>
          ) : (
            pipelineData.attribution.ranking.map((candidate, index) => (
              <div key={candidate.mmsi} style={{ marginBottom: '15px', padding: '10px', backgroundColor: 'rgba(30, 41, 59, 0.5)', borderRadius: '4px', borderLeft: `3px solid ${index === 0 ? '#f59e0b' : '#64748b'}` }}>
                <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '5px', display: 'flex', justifyContent: 'space-between' }}>
                  <span>#{index + 1} {candidate.name}</span>
                  <span style={{ color: index === 0 ? '#f59e0b' : '#94a3b8' }}>{candidate.total_score}/100</span>
                </div>
                <div style={{ fontSize: '11px', lineHeight: '1.5', color: '#cbd5e1' }}>
                  <div>Spatial: {candidate.spatial} | Temporal: {candidate.temporal}</div>
                  <div>Trajectory: {candidate.trajectory} | Drift: {candidate.drift}</div>
                  <div>Behavioral: {candidate.behavioral} | AIS: {candidate.ais}</div>
                  {candidate.is_dark_vessel && <div style={{ color: '#ef4444', fontWeight: 'bold', marginTop: '4px' }}>⚠️ AIS GAP DETECTED</div>}
                </div>
                {index === 0 && (
                  <button onClick={() => setShowEvidenceModal(true)} style={{ marginTop: '8px', width: '100%', padding: '6px', backgroundColor: '#3b82f6', color: '#f8fafc', border: 'none', borderRadius: '4px', fontSize: '11px', fontWeight: 'bold', cursor: 'pointer' }}>VIEW EXPLANATION & EVIDENCE</button>
                )}
              </div>
            ))
          )}
        </div>
      </div>
      <style>{`@keyframes pulse-red { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.2); } }`}</style>
    </div>
  );
}
export default App;

