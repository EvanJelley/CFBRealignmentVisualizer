import { useEffect, useState, useRef } from 'react'
import './App.css'
import axios from 'axios'
import {
  MapContainer,
  TileLayer,
  useMap,
  Marker,
  Popup
} from 'react-leaflet'
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import Draggable from 'react-draggable';

const APIURL = 'http://localhost:8000'
const TEAMLOGOSIZE = 14
const CONFLOGOSIZE = 22



function App() {

  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [conferenceList, setConferenceList] = useState([])
  const [filteredConferenceList, setFilteredConferenceList] = useState([])
  const [conferenceIcons, setConferenceIcons] = useState({})
  const [conferenceLogos, setConferenceLogos] = useState({})
  const [schoolIcons, setSchoolIcons] = useState({})


  const [conferenceNames, setConferenceNames] = useState([])
  const [selectedConference, setSelectedConference] = useState('')
  const [conferenceYears, setConferenceYears] = useState([])
  const [selectedYear, setSelectedYear] = useState('')


  const getConferences = async () => {
    try {
      setIsLoading(true)
      const response = await axios.get(APIURL + '/api/conferencebyyear/')
      setConferenceList(response.data)

      let conferenceNameList = []
      response.data.map((conference) => {
        conferenceNameList.includes(conference.conference) ? null :
          conferenceNameList.push(conference.conference)
      });
      conferenceNameList.push('NCAA')
      setConferenceNames(conferenceNameList)

      setSelectedConference(conferenceNameList[0])

      const logoResponse = await axios.get(APIURL + '/api/conferencelogos/')
      let logos = {};
      logoResponse.data.forEach((logo) => {
        logos[logo.name] = logo.logo;
      });
      setConferenceLogos(logos);
      let confIcons = {};
      logoResponse.data.forEach((logo) => {
        getImageDimmensions(logo.logo, CONFLOGOSIZE).then((dimmensions) => {
          confIcons[logo.name] = L.icon({
            iconUrl: logo.logo,
            iconSize: dimmensions
          });
        });
      });
      setConferenceIcons(confIcons);

      const responseSchools = await axios.get(APIURL + '/api/schoollogos/')
      let schoolIcons = {};
      responseSchools.data.forEach((school) => {
        school.logo = school.logo
        getImageDimmensions(school.logo, TEAMLOGOSIZE).then((dimmensions) => {
          schoolIcons[school.name] = L.icon({
            iconUrl: school.logo,
            iconSize: dimmensions,
          });
        });
      });
      setSchoolIcons(schoolIcons);

      console.log('Getting Conferences...')
    } catch (error) {
      setHasError(true)
      console.error(error)
    } finally {
      setIsLoading(false)
    }
  }

  const getImageDimmensions = (url, pixels) => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.src = url;
      img.onload = () => {
        let width = img.width;
        let height = img.height;
        let aspectRatio = width / height;
        aspectRatio > 3 ? pixels *= .7 : null;
        img.width > img.height ? resolve([Math.round(pixels * aspectRatio), pixels]) : resolve([pixels, Math.round(pixels / aspectRatio)]);
      };
      img.onerror = () => {
        reject('error');
      };
    });
  };

  useEffect(() => {
    getConferences()
  }, [])

  let selectConferenceHandler = (e) => {
    const button = e.target.closest('button');
    const conferenceName = button.getAttribute('data-conf-name');
    console.log(conferenceName)
    setSelectedConference(conferenceName)
  }

  let selectYearHandler = (e) => {
    setSelectedYear(e.target.value)
  }

  let conferenceFilter = () => {
    if (selectedConference == 'NCAA') {
      let filteredList = conferenceList.filter((conference) => {
        return conference.year == selectedYear
      })
      setFilteredConferenceList(filteredList)
    } else {
      let filteredList = conferenceList.filter((conference) => {
        return conference.year == selectedYear && conference.conference == selectedConference
      })
      setFilteredConferenceList(filteredList)
    };
  }

  useEffect(() => {
    conferenceFilter()
  }, [selectedYear])

  useEffect(() => {
    if (selectedConference == 'NCAA') {
      let years = []
      conferenceList.map((conference) => {
        !years.includes(conference.year) ? years.push(conference.year) : null
      });
      years.sort()
      setConferenceYears(years)
      conferenceFilter()
    } else {
      let years = []
      conferenceList.map((conference) => {
        conference.conference == selectedConference && !years.includes(conference.year) ? years.push(conference.year) : null
      });
      years.sort()
      setConferenceYears(years)
      years.includes(Number(selectedYear)) ? conferenceFilter() : setSelectedYear(years[0])
    }
  }, [selectedConference])

  var myIcon = L.icon({
    iconUrl: APIURL + '/media/images/conf_logos/ncaa.png',
    iconSize: [10, 10],
  });

  const usaBounds = [
    [5.499550, -167.276413],
    [83.162102, -52.233040]
  ];

  return (
    <>
      <div className='container'>
        <h1>Conference Realignment Map</h1>
        {isLoading ?
          <p>Loading...</p>
          :
          <>
            <OptionBay conferenceNames={conferenceNames}
              conferenceYears={conferenceYears}
              selectConference={selectConferenceHandler}
              selectYear={selectYearHandler}
              conferenceLogosObject={conferenceLogos} />
            <div className='row'>
              <div className='col-12'>
                <MapContainer style={{ height: "24rem", width: "100%" }} center={[37.0902, -95.7129]} zoom={4}
                  scrollWheelZoom={false} maxBounds={usaBounds} dragging={false} zoomControl={false}>
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                  {selectedConference == 'NCAA' ?
                    filteredConferenceList.map((conference) => conference.schools.map((school) => (
                      <Marker key={`${school.name}-${school.id}`} position={[Number(school.latitude), Number(school.longitude)]}
                        icon={conferenceIcons[conference.conference] || myIcon}>
                        <Popup>
                          {school.name} - {school.city}, {school.state}
                        </Popup>
                      </Marker>
                    ))
                    )
                    :
                    filteredConferenceList.map((conference) => conference.schools.map((school) => (
                      <Marker key={`${school.name}-${school.id}`} position={[Number(school.latitude), Number(school.longitude)]}
                        icon={schoolIcons[school.name] || myIcon}>
                        <Popup>
                          {school.name} - {school.city}, {school.state}
                        </Popup>
                      </Marker>
                    ))
                    )}
                  {filteredConferenceList.map((conference) => (
                    <Marker key={`${conference.capital.name}-${conference.id}`}
                      position={[Number(conference.capital.latitude), Number(conference.capital.longitude)]}
                      icon={conferenceIcons[conference.conference] || myIcon}>
                      <Popup>
                        Proposed {conference.conference} Capital: {conference.capital.name} - {conference.capital.state}
                      </Popup>
                    </Marker>
                  ))}
                </MapContainer>
              </div>
            </div><ul>
              {filteredConferenceList.map((conference) => (
                <li key={conference.id}>
                  {conference.conference} - {conference.year}
                  <ul>
                    <li>Average School Distance from Center: {conference.avgDistanceFromCenter} miles</li>
                    <li>Average Distance Between Schools: {conference.avgDistanceBetweenSchools} miles</li>
                    <li>Proposed Capital: {conference.capital.name} - {conference.capital.state}</li>
                  </ul>
                </li>
              ))}
            </ul></>
        }
      </div>
    </>
  )
}

function OptionBay({ conferenceNames, conferenceYears, selectConference, selectYear, conferenceLogosObject, selectedYear }) {
  return (
    <>
      <div className='row'>
        <div className='col-12'>
          <h3>Option Bay</h3>
          <div className='conference-buttons-bay'>
            {conferenceNames.map((conferenceName) => (
              <button key={conferenceName} onClick={selectConference} data-conf-name={conferenceName} className='conference-selection-button'>
                <img src={conferenceLogosObject[conferenceName]} alt={conferenceName} className='conference-selection-img' />
              </button>
            ))}
          </div>
          <DraggableDot x={0} y={0} />
        </div>
      </div>
    </>
  )
}

const DraggableDot = ({ x, y, years }) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const lineDotRef = useRef(null);
  const [bounds, setBounds] = useState({ left: 0, right: 0, top: 0, bottom: 0 });
  const dotRadius = 10;

  useEffect(() => {
    if (!lineDotRef.current) return;
    const { width } = lineDotRef.current.getBoundingClientRect();
    setBounds({ left: 0, right: width - (dotRadius * 2), top: 0, bottom: 0 });
  }, []);


  const dragFunction = (e, data) => {
    setPosition({ x: data.x, y: 0 });
  }

  return (
    <div className='line-dot'
      ref={lineDotRef}
      style={{
        width: "100%",
        border: '1px solid black'
      }}>
      <Draggable
        position={position}
        onDrag={dragFunction}
        bounds={bounds}
      >
        <div
          style={{
            width: String(dotRadius * 2) + 'px',
            height: String(dotRadius * 2) + 'px',
            background: 'red',
            borderRadius: '50%',
            cursor: 'grab',
          }}
        />
      </Draggable>
    </div>
  );
}

const DraggableTimeline = ({ conferenceYears, selectYear, selectedYear }) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const handleDrag = (e, data) => {
    setPosition({ x: data.x, y: 0 });
    // Determine the year based on the drag position
    const index = Math.round(data.x / 50); // Assuming each year takes 50px of space
    const newIndex = Math.max(0, Math.min(conferenceYears.length - 1, index));
    selectYear(conferenceYears[newIndex]);
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', width: '100%', overflow: 'hidden' }}>
      <Draggable axis="x" position={position} onDrag={handleDrag} bounds="parent">
        <div style={{ display: 'flex' }}>
          {conferenceYears.map((year, index) => (
            <div
              key={year}
              style={{
                padding: '10px',
                width: '50px',
                textAlign: 'center',
                background: selectedYear === year ? 'lightblue' : 'white',
                border: '1px solid #ccc',
              }}
            >
              {year}
            </div>
          ))}
        </div>
      </Draggable>
    </div>
  );
};

export default App
