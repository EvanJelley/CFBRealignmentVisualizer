import { useEffect, useState, useRef } from 'react'
import './App.css'
import axios from 'axios'
import {
  MapContainer,
  TileLayer,
  useMap,
  Marker,
  Popup,
} from 'react-leaflet'
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import Draggable from 'react-draggable';

const vpWidth = window.innerWidth;

const calculateTeamIconSize = () => {
  if (vpWidth < 768) return 10;
  if (vpWidth < 1500) return 14;
  return 20;
};

const calculateConfIconSize = () => {
  if (vpWidth < 768) return 14;
  if (vpWidth < 1500) return 22;
  return 30;
};

const APIURL = 'http://localhost:8000';
const TEAMLOGOSIZE = calculateTeamIconSize();
const CONFLOGOSIZE = calculateConfIconSize();

const footballImage = "/images/football.png";
const basketballImage = "/images/basketball.png";
const githubLogo = "/images/github.png";


function App() {

  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [conferenceList, setConferenceList] = useState([])
  const [filteredConferenceList, setFilteredConferenceList] = useState([])
  const [conferenceIcons, setConferenceIcons] = useState({})
  const [conferenceLogos, setConferenceLogos] = useState({})
  const [schoolIcons, setSchoolIcons] = useState({})
  const [animate, setAnimate] = useState(false)


  const [conferenceNames, setConferenceNames] = useState([])
  const [selectedConference, setSelectedConference] = useState('')
  const [conferenceYears, setConferenceYears] = useState([])
  const [selectedYear, setSelectedYear] = useState('')
  const [sport, setSport] = useState('football')
  const [splitConference, setSplitConference] = useState(false)


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

  const sportHandler = (e) => {
    const button = e.target.closest('button');
    const sport = button.textContent.toLowerCase().trim();
    setSport(sport)
  }

  const splitConferenceMonitor = () => {
    let split = false;
    filteredConferenceList.map((conference) => {
      conference.football && conference.basketball ? null : split = true
    });
    setSplitConference(split)
  }

  let selectConferenceHandler = (e) => {
    const button = e.target.closest('button');
    const conferenceName = button.getAttribute('data-conf-name');
    setSelectedConference(conferenceName)
  }

  let selectYearHandler = (year) => {
    setSelectedYear(year)
  }

  const yearSearch = (e) => {
    let year = e.target.value;
    year.length == 4 && !isNaN(year) && year >= conferenceYears[0] && year <= conferenceYears[conferenceYears.length - 1]
      ? setSelectedYear(year) : null
  }

  let conferenceFilter = () => {
    if (sport == 'football') {
      if (selectedConference == 'NCAA') {
        let filteredList = conferenceList.filter((conference) => {
          return conference.year == selectedYear && conference.football
        })
        setFilteredConferenceList(filteredList)
      } else {
        let filteredList = conferenceList.filter((conference) => {
          return conference.year == selectedYear && conference.conference == selectedConference && conference.football
        })
        setFilteredConferenceList(filteredList)
      };
    } else {
      if (selectedConference == 'NCAA') {
        let filteredList = conferenceList.filter((conference) => {
          return conference.year == selectedYear && conference.basketball
        })
        setFilteredConferenceList(filteredList)
      } else {
        let filteredList = conferenceList.filter((conference) => {
          return conference.year == selectedYear && conference.conference == selectedConference && conference.basketball
        })
        setFilteredConferenceList(filteredList)
      };
    }
    splitConferenceMonitor()
  }

  useEffect(() => {
    conferenceFilter()
  }, [selectedYear, sport])

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

  const animationHandler = () => {
    setAnimate(!animate)
  }

  useEffect(() => {
    if (animate) {
      setTimeout(() => {
        setSelectedYear(selectedYear + 1)
      }, 1000)
    } else {
      clearTimeout()
    }
  }, [animate])

  var myIcon = L.icon({
    iconUrl: APIURL + '/media/images/conf_logos/ncaa.png',
    iconSize: [10, 10],
  });

  return (
    <>
      {isLoading ?
        <p>Loading...</p>
        :
        <>
          <NavBar conferenceNames={conferenceNames}
            conferenceYears={conferenceYears}
            selectConference={selectConferenceHandler}
            searchYears={yearSearch}
            conferenceLogosObject={conferenceLogos}
            selectedYear={selectedYear}
            sportHandler={sportHandler}
            splitConference={splitConference} 
            setAnimation={animationHandler}/>
          <OptionBay conferenceNames={conferenceNames}
            conferenceYears={conferenceYears}
            selectConference={selectConferenceHandler}
            selectYear={selectYearHandler}
            conferenceLogosObject={conferenceLogos}
            selectedYear={selectedYear}
            sportHandler={sportHandler}
            splitConference={splitConference} />
          <Map filteredConferenceList={filteredConferenceList}
            conferenceIcons={conferenceIcons}
            schoolIcons={schoolIcons}
            selectedConference={selectedConference} />
          <ConferenceDetails conference={filteredConferenceList[0]} />
        </>
      }
    </>
  )
}

function OptionBay({ conferenceNames, conferenceYears, selectConference, selectYear, conferenceLogosObject, selectedYear, sportHandler, splitConference }) {
  return (
    <>
      <div className='row'>
        <div className='col-12'>
          {/* {splitConference ?
            <div className='sport-buttons-bay'>
              <button onClick={sportHandler} className='sport-selection-button'>Basketball</button>
              <button onClick={sportHandler} className='sport-selection-button'>Football</button>
            </div>
            : null} */}
          <DraggableDot years={conferenceYears} setYear={selectYear} selectedYear={selectedYear} />
        </div>
      </div>
    </>
  )
}

function NavBar({ conferenceNames, conferenceYears, selectConference, searchYears, conferenceLogosObject, selectedYear, sportHandler, splitConference, setAnimation}) {

  return (
    <>
      <nav className="navbar navbar-expand-lg bg-primary navbar-dark " >
        <div className="container-fluid">
          < a className="navbar-brand" href="#"> CFB Realignment Map</a >
          <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent"
            aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <i className="fas fa-bars">Menu</i>
          </button >
          <div className="collapse navbar-collapse" id="navbarSupportedContent" >
            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
              <li className="nav-item">
                <a className="nav-link" href="#">About</a>
              </li>
              <li className="nav-item dropdown">
                <a className="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button"
                  data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                  Conferences
                </a>
                <ul className="dropdown-menu list-inline dropdown-menu-conferences" aria-labelledby="navbarDropdown">
                  {conferenceNames.map((conferenceName) => (
                    <li key={conferenceName} className='list-inline-item'>
                      <button style={{ height: "3.7rem" }} onClick={selectConference} data-conf-name={conferenceName} className='dropdown-item'>
                        <img src={conferenceLogosObject[conferenceName]} alt={conferenceName}
                          className='conference-selection-img' />
                      </button>
                    </li>
                  ))}
                </ul>
              </li>
              <li className="nav-item dropdown">
                <a className="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button"
                  data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                  Sports
                </a>
                <ul className="dropdown-menu" aria-labelledby="navbarDropdown">
                  <li key={'football'} className='dropdown-item'>
                    <button onClick={sportHandler} className='dropdown-item'>
                      <img src={footballImage} alt='football' className='sport-selection-img' /> Football
                    </button>
                  </li>
                  <li key={'basketball'} className='dropdown-item'>
                    <button onClick={sportHandler} className='dropdown-item'>
                      <img src={basketballImage} alt='basketball' className='sport-selection-img' /> Basketball
                    </button>
                  </li>
                </ul>
              </li>
              <li className="nav-item">
                <button className='nav-link' onClick={setAnimation}>Animate</button>
              </li>
                
            </ul>
          </div>

          {/* Icons --- ADD GITHUB */}
          <ul className="navbar-nav d-flex flex-row me-1">
            <li className="nav-item me-3 me-lg-0">
              <a className="nav-link" href="https://github.com/EvanJelley/CFBRealignmentVisualizer" target="_blank" rel="noopener noreferrer">
                <img src={githubLogo} alt='GitHub' className='navbar-logo' />
              </a>
            </li>
            <li className="nav-item me-3 me-lg-0">
              <a className="nav-link" href="#"><i className="fab fa-twitter"></i></a>
            </li>
          </ul>

          {/* Search */}
          <form className="w-auto" onChange={searchYears} onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
            }
          }}>
            <input type="search" className="form-control" placeholder="Type a Year" aria-label="Search" />
          </form>
        </div >
        {/* Container wrapper */}
      </nav >
    </>
  )
}


const DraggableDot = ({ years, setYear, selectedYear }) => {

  let yearRange = Math.abs(years[0] - years[years.length - 1]);

  const nodeRef = useRef(null);
  const [position, setPosition] = useState({ x: 0, y: 0, percentPosition: 0 });
  const lineDotRef = useRef(null);
  const [prevYear, setPrevYear] = useState(selectedYear);
  const [draggableKey, setDraggableKey] = useState(0);
  const [bounds, setBounds] = useState({ left: -100, right: 100, top: 0, bottom: 0 });
  const yearWidth = 50;


  const updateBounds = () => {
    if (!lineDotRef.current) return console.log('No ref');
    let totalYearsWidth = yearWidth * yearRange;
    let leftBound = -(totalYearsWidth + yearWidth);
    setBounds({ left: leftBound, right: 1, top: 0, bottom: 0 });
  };

  useEffect(() => {
    updateBounds();
    const newX = -(selectedYear - years[0]) * yearWidth - yearWidth / 2;
    setPosition({ x: newX, y: 0, percentPosition: newX / bounds.left });
    setPrevYear(selectedYear);
  }, [yearRange]);

  useEffect(() => {
    if (Math.abs(selectedYear - prevYear) > 1) {
      console.log('Year Jump')
      setDraggableKey(draggableKey + 1);
      const newX = -(selectedYear - years[0]) * yearWidth - yearWidth / 2;
      setPosition({ x: newX, y: 0, percentPosition: newX / bounds.left });
      setPrevYear(selectedYear);
    } else {
      setPrevYear(selectedYear);
    }
  }, [selectedYear]);

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
    const newPostion = { x: data.x, y: 0, percentPosition: data.x / bounds.left }
    setPosition(newPostion);

    const index = Math.floor((data.x / bounds.left) * (years.length));
    const safeIndex = index < 0 ? 0 : index >= years.length ? years.length - 1 : index;
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
        <Draggable axis="x" bounds={bounds} onDrag={handleDrag} position={position} nodeRef={nodeRef} key={draggableKey}>
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
                    background: selectedYear == year ? 'lightblue' : 'white',
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
};

function Map({ filteredConferenceList, conferenceIcons, schoolIcons, selectedConference }) {


  const mapParams = {
    center: [37.5, -95.7129],
    zoom: 4,
    scrollWheelZoom: false,
    dragging: false,
    zoomControl: false,
    doubleClickZoom: false,
    vpHeight: 50,
  };

  const mapRef = useRef(null);
  const containerRef = useRef(null);

  const calculateZoomLevel = () => {
    if (vpWidth < 768) return 3;
    if (vpWidth < 1500) return 4;
    return 5;
  };

  const calculateHeight = () => {
    if (vpWidth < 768) return 33;
    if (vpWidth < 1500) return 50;
    return 75;
  };

  const handleResize = () => {
    if (mapRef.current) {
      const { current: map } = mapRef;
      const zoom = calculateZoomLevel();
      map.setView([0, 0], zoom);
    }
  };

  useEffect(() => {
    const observer = new ResizeObserver(handleResize);
    if (containerRef.current) {
      observer.observe(containerRef.current);
    }
    handleResize();

    return () => {
      if (containerRef.current) {
        observer.unobserve(containerRef.current);
      }
    };
  }, []);


  return (
    <div className='row'>
      <div className='col-12' ref={containerRef}>
        <MapContainer
          center={[37.8, -96]}
          zoom={calculateZoomLevel()}
          style={{ height: `${calculateHeight()}vh`, width: '100%' }}
          scrollWheelZoom={mapParams.scrollWheelZoom}
          dragging={mapParams.dragging}
          zoomControl={mapParams.zoomControl}
          doubleClickZoom={mapParams.doubleClickZoom}
          whenCreated={(mapInstance) => { mapRef.current = mapInstance; handleResize(); }}>
          <TileLayer
            attribution='&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url='https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png'
          />
          {selectedConference == 'NCAA' ?
            filteredConferenceList.map((conference) => conference.schools.map((school) => (
              <Marker key={`${school.name}-${school.id}`} position={[Number(school.latitude), Number(school.longitude)]}
                icon={conferenceIcons[conference.conference] || myIcon} zIndexOffset={1000}>
                <Popup>
                  {school.name} - {school.city}, {school.state}
                </Popup>
              </Marker>
            ))
            )
            :
            filteredConferenceList.map((conference) => conference.schools.map((school) => (
              <Marker key={`${school.name}-${school.id}`} position={[Number(school.latitude), Number(school.longitude)]}
                icon={schoolIcons[school.name]} zIndexOffset={1000}>
                <Popup>
                  {school.name} - {school.city}, {school.state}
                </Popup>
              </Marker>
            ))
            )}
          {filteredConferenceList.map((conference) => (
            <Marker key={`${conference.capital.name}-${conference.id}`}
              position={[Number(conference.capital.latitude), Number(conference.capital.longitude)]}
              icon={conferenceIcons[conference.conference]} zIndexOffset={500}>
              <Popup>
                Proposed {conference.conference} Capital: {conference.capital.name} - {conference.capital.state}
              </Popup>
            </Marker>
          ))}
          {filteredConferenceList.map((conference) => (conference.schools.map((school) => (
            school.name.includes('Hawai') ? <HawaiiMapOverlay school={school} schoolIcons={schoolIcons} /> : null)
          )))}
        </MapContainer>
      </div>
    </div>
  )
};

const HawaiiMapOverlay = ({ school, schoolIcons }) => {
  const hawaiiCenter = [20.7984, -157]; // Center coordinates for Hawaii

  const calculateHeight = () => {
    if (vpWidth < 768) return 12;
    if (vpWidth < 1500) return 12;
    return 37;
  };

  const calculateWidth = () => {
    if (vpWidth < 768) return 12;
    if (vpWidth < 1500) return 12;
    return 37;
  }

  const calculateZoomLevel = () => {
    if (vpWidth < 768) return 4;
    if (vpWidth < 1500) return 4;
    return 6;
  };

  return (
    <MapContainer
      className='hawaii-map-overlay'
      center={hawaiiCenter}
      zoom={calculateZoomLevel()}
      style={{ height: `${calculateHeight()}vh`, width: `${calculateWidth()}vw`, position: 'absolute', bottom: '10px', left: '10px', zIndex: 1000 }}
      scrollWheelZoom={false}
      dragging={false}
      zoomControl={false}
      doubleClickZoom={false}
    >
      <TileLayer
        url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png' id='HawaiiAttribution'
      />
      <Marker key={school.id} position={[Number(school.latitude), Number(school.longitude)]} icon={schoolIcons[school.name]}>
      </Marker>
    </MapContainer>
  );
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


// center={mapParams.center} 
// zoom={mapParams.zoom}
// scrollWheelZoom={mapParams.scrollWheelZoom} 
// maxBounds={mapParams.maxBounds} 
// dragging={mapParams.dragging} 
// zoomControl={mapParams.zoomControl} 
// ref={mapRef}

// const usaBounds = [
//   [5.499550, -167.276413],
//   [83.162102, -52.233040]
// ];