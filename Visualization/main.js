import './style.css';
import Map from 'ol/Map.js';
import OSM from 'ol/source/OSM.js';
import TileLayer from 'ol/layer/Tile.js';
import View from 'ol/View.js';
import {fromLonLat} from 'ol/proj.js';
import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';
import VectorLayer from 'ol/layer/Vector';
import {Vector as VectorSource} from 'ol/source';

const vectorSource = new VectorSource();

const marker = new Feature({
  geometry: new Point(fromLonLat([-96, 39.8283]))
});

vectorSource.addFeature(marker);

const vectorLayer = new VectorLayer({
  source: vectorSource
});

const map = new Map({
  target: 'map',
  layers: [
    new TileLayer({
      source: new OSM()
    }),
    vectorLayer,
  ],
  view: new View({
    center: fromLonLat([-96, 39.8283]),
    zoom: 4.75
  })
});