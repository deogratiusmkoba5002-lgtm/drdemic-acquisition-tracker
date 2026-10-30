const map = L.map("map", { preferCanvas: true }).setView([-6.79, 39.21], 11);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "&copy; OpenStreetMap contributors"
}).addTo(map);

async function loadSchools() {
  const response = await fetch ("/api/schools");

  if(!response.ok) {
    throw new Error ("Could not load schools");
  }
  const schools = await response.json();
  return schools
}

function buildPopup(school) {
  const element = document.createElement("div");
  element.textContent = school.name + " | " + (school.ownership || "Unknown") + " | " + school.status;
  return element
}

async function showSchools() {
  const schools = await loadSchools();
  for (const school of schools) {
    const pointMarker = L.circleMarker([school.lat, school.lng], {
      radius: 6,
      color: school.visited ? "green" : "red",
      fillOpacity: 0.8
    }).addTo(map);
    pointMarker.bindPopup(buildPopup(school));
  }
}

showSchools().catch(error => {console.error(error);});
