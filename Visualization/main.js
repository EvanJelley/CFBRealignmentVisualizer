// import './style.css';
import Map from 'ol/Map.js';
import OSM from 'ol/source/OSM.js';
import TileLayer from 'ol/layer/Tile.js';
import View from 'ol/View.js';
import { fromLonLat } from 'ol/proj.js';
import Feature from 'ol/Feature.js';
import Point from 'ol/geom/Point.js';
import VectorLayer from 'ol/layer/Vector.js';
import { Vector as VectorSource } from 'ol/source.js';
import Papa from 'papaparse';
// import fs from 'fs';

const vectorSource = new VectorSource();

// const file = fs.createReadStream('practiceBigTen.csv');

fetch('../practiceBigTen.csv')
  .then(response => response.text())
  .then(csvString => {
    Papa.parse(csvString, {
      complete: (results) => {
        for (let i of results.data) {
          let lat = i[4]
          let lon = i[5]
          console.log(lat, lon)
          const marker = new Feature({
            geometry: new Point(fromLonLat([lon, lat]))
          });
          vectorSource.addFeature(marker);
        }
      }
    }); console.log(csvString);
  })
  .catch(error => console.error('Error fetching CSV:', error));


// client.open('GET', '//FinalConferenceCSVs/BigTen.csv');
// client.onload = function () {
//   const csv = client.responseText;
//   const data = d3.csvParse(csv);
//   console.log(data);
//   for (let i = 0; i < data.length; i++) {
//     const lon = data[i].Longitude;
//     const lat = data[i].Latitude;
//     const marker = new Feature({
//       geometry: new Point(fromLonLat([lon, lat]))
//     });
//     vectorSource.addFeature(marker);
//   }
// }``

// const marker = new Feature({
//   geometry: new Point(fromLonLat([-96, 39.8283]))
// });

// vectorSource.addFeature(marker);



// const vectorLayer = new VectorLayer({
//   source: vectorSource
// });

// const map = new Map({
//   target: 'map',
//   layers: [
//     new TileLayer({
//       source: new OSM()
//     }),
//     vectorLayer,
//   ],
//   view: new View({
//     center: fromLonLat([-96, 39.8283]),
//     zoom: 4.75
//   })
// });
