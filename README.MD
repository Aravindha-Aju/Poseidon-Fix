Save the following code blocks to their respective paths in your local Poseidon repository




THEN
...............................................

Install Dependencies:


pip install fastapi uvicorn pydantic shapely
cd frontend && npm install react-leaflet leaflet @turf/turf



Start Backend:

uvicorn backend.main:app --reload --port 8000


To Start Frontend:

cd frontend && npm run dev


Open http://localhost:5173 (or your Vite port).
Click "RUN INVESTIGATION".
Observe the backend logs showing the sequential execution of Detection → Drift → Behavior → Attribution → Impact → Evidence.
The UI will display OCEAN PIONEER as the Top Candidate with a score of 88/100, dynamically generated explanation, and an explicit "⚠ AIS GAP DETECTED" warning.
Click "DOWNLOAD EVIDENCE PACKAGE" to verify the SHA-256 hashes are generated from real serialized JSON.


