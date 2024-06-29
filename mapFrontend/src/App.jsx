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

      const confIconsPromises = logoResponse.data.map(async (logo) => {
        const dimensions = await getImageDimmensions(logo.logo, CONFLOGOSIZE);
        return { name: logo.name, icon: L.icon({ iconUrl: logo.logo, iconSize: dimensions }) };
      });
      const confIconsArray = await Promise.all(confIconsPromises);
      let confIcons = {};
      confIconsArray.forEach(item => {
        confIcons[item.name] = item.icon;
      });
      setConferenceIcons(confIcons);

      const responseSchools = await axios.get(APIURL + '/api/schoollogos/')
      const schoolIconsPromises = responseSchools.data.map(async (school) => {
        const dimensions = await getImageDimmensions(school.logo, TEAMLOGOSIZE);
        return { name: school.name, icon: L.icon({ iconUrl: school.logo, iconSize: dimensions }) };
      });
      const schoolIconsArray = await Promise.all(schoolIconsPromises);
      let schoolIcons = {};
      schoolIconsArray.forEach(item => {
        schoolIcons[item.name] = item.icon;
      });
      setSchoolIcons(schoolIcons);

      // console.log('Getting Conferences...')
    } catch (error) {
      setHasError(true)
      console.error(error)
    } finally {
      // console.log('Finished Getting Conferences')
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
    setSelectedConference(conferenceName)
  }

  let selectYearHandler = (year) => {
    setSelectedYear(year)
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
              conferenceLogosObject={conferenceLogos}
              selectedYear={selectedYear} />
            <Map filteredConferenceList={filteredConferenceList}
              conferenceIcons={conferenceIcons}
              schoolIcons={schoolIcons}
              selectedConference={selectedConference} />
            <ConferenceDetails conference={filteredConferenceList[0]} />
          </>
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
          <DraggableDot years={conferenceYears} setYear={selectYear} selectedYear={selectedYear} />
        </div>
      </div>
    </>
  )
}

const DraggableDot = ({ years, setYear, selectedYear }) => {

  let yearRange = Math.abs(years[0] - years[years.length - 1]);

  const nodeRef = useRef(null);
  const [position, setPosition] = useState({ x: 0, y: 0, percentPosition: 0});
  const [yearPosition, setYearPosition] = useState(0);
  const lineDotRef = useRef(null);
  const [bounds, setBounds] = useState({ left: -100, right: 100, top: 0, bottom: 0 });
  const yearWidth = 50;


  const updateBounds = () => {
    if (!lineDotRef.current) return console.log('No ref');
    let totalYearsWidth = yearWidth * yearRange;
    let leftBound = -(totalYearsWidth + yearWidth);
    setBounds({ left: leftBound, right: 1, top: 0, bottom: 0 });
    // setPosition({ x: 0, y: 0, percentPosition: 0 });
  };

  useEffect(() => {
    updateBounds();
  }, [yearRange]);


  useEffect(() => {

    updateBounds();

    const resizeObserver = new ResizeObserver(() => {
      updateBounds();
    });

    if (lineDotRef.current) {
      resizeObserver.observe(lineDotRef.current);
    }

    return () => {
      if (lineDotRef.current) {
        resizeObserver.unobserve(lineDotRef.current);
      }
      resizeObserver.disconnect();
    };
  }, [lineDotRef.current]);

  const handleDrag = (e, data) => {
    // const xMove = Math.abs(data.x);
    // const newPostion = { x: data.x, y: 0, percentPosition: data.x/ bounds.left }
    // console.log(newPostion)
    // setPosition(newPostion);

    // Calculate the index based on the percentage position
    const index = Math.floor((data.x/ bounds.left) * (years.length));

    // Ensure the index is within the bounds of the years array
    const safeIndex = index < 0 ? 0 : index >= years.length ? years.length - 1 : index;

    // Call setYear with the year value directly
    setYear(years[safeIndex]);
  };

  return (
    <>
      <div className='line-dot'
        ref={lineDotRef}
        style={{
          width: "100%",
          height: '30px',
          border: '1px solid black',
          overflow: 'hidden',
          position: 'relative',
        }}>
          {console.log("bounds", bounds)}
        <Draggable axis="x" bounds={bounds} onDrag={handleDrag} defaultPosition={{ x: yearPosition, y: position.y}} nodeRef={nodeRef}>
          <div style={{ display: 'inline-block', overflow: 'hidden', whiteSpace: "nowrap", position: "absolute", left: "50%" }} ref={nodeRef}>
            {
              years.map((year, index) => (
                <div
                  key={year}
                  style={{
                    width: `${yearWidth}px`,
                    height: '30px',
                    display: 'inline-block',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: selectedYear === year ? 'lightblue' : 'white',
                    border: '1px solid #ccc',
                  }}
                >
                  {year}
                </div>
              ))}
          </div>
        </Draggable >
      </div >
      <div className="yearSelectorTriangle">
        <div
          className="triangle"
          style={{
            width: 0,
            height: 0,
            margin: 'auto',
            borderLeft: '10px solid transparent',
            borderRight: '10px solid transparent',
            borderBottom: '10px solid black',
            position: 'relative',
          }}
        ></div>
      </div>
    </>
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
              {/* {year} */}
            </div>
          ))}
        </div>
      </Draggable>
    </div>
  );
};


function Map({ filteredConferenceList, conferenceIcons, schoolIcons, selectedConference }) {
  const usaBounds = [
    [5.499550, -167.276413],
    [83.162102, -52.233040]
  ];

  return (
    <div className='row'>
      <div className='col-12'>
        <MapContainer style={{ height: "23.5rem", width: "100%" }} center={[37.5, -95.7129]} zoom={4}
          scrollWheelZoom={false} maxBounds={usaBounds} dragging={false} zoomControl={false}>
          <TileLayer
            attribution='&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url='https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png'
          />
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
                icon={schoolIcons[school.name]}>
                <Popup>
                  {school.name} - {school.city}, {school.state}
                </Popup>
              </Marker>
            ))
            )}
          {filteredConferenceList.map((conference) => (
            <Marker key={`${conference.capital.name}-${conference.id}`}
              position={[Number(conference.capital.latitude), Number(conference.capital.longitude)]}
              icon={conferenceIcons[conference.conference]}>
              <Popup>
                Proposed {conference.conference} Capital: {conference.capital.name} - {conference.capital.state}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  )
};

function ConferenceDetails({ conference }) {
  return (
    <div>
      <h3>{conference.conference} - {conference.year}</h3>
      <ul>
        <li>Average School Distance from Center: {conference.avgDistanceFromCenter} miles</li>
        <li>Average Distance Between Schools: {conference.avgDistanceBetweenSchools} miles</li>
        <li>Proposed Capital: {conference.capital.name} - {conference.capital.state}</li>
      </ul>
    </div>
  )
};

export default App
