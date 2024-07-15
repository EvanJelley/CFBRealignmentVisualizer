import { useEffect, useState, useRef } from 'react'
import './App.css'
import axios from 'axios'
import {
  MapContainer,
  TileLayer,
  useMap,
  Marker,
  Popup,
  Polygon,
  Polyline,
  Circle,
} from 'react-leaflet'
import 'leaflet/dist/leaflet.css';
import L, { map } from 'leaflet';
import Draggable from 'react-draggable';
import { Line } from 'react-chartjs-2';
import Chart from "chart.js/auto";
import { CategoryScale, plugins } from "chart.js";

Chart.register(CategoryScale);

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
const playImage = "/images/play.png";
const githubLogo = "/images/github.png";
const pauseImage = "/images/pause.png";

const chartOptions = {
  aspectRatio: 1.7,
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    y: {
      title: {
        display: true,
        text: 'Miles', // Label for the y-axis
        color: '#00254c', // Optional: you can style the label color
        font: {
          size: 16 // Optional: you can set the font size
        }
      }
    },
  },
};

function App() {

  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [conferenceList, setConferenceList] = useState([])
  const [filteredConferenceList, setFilteredConferenceList] = useState([])
  const [conferenceIcons, setConferenceIcons] = useState({})
  const [conferenceLogos, setConferenceLogos] = useState({})
  const [schoolIcons, setSchoolIcons] = useState({})
  const [conferenceColors, setConferenceColors] = useState([])
  const [chartData, setChartData] = useState({})

  const [animate, setAnimate] = useState(false)
  const [redrawTimelineBool, setRedrawTimelineBool] = useState(false)
  const animateRef = useRef(animate)
  const [animationSpeed, setAnimationSpeed] = useState(500)
  const [mapDisplay, setMapDisplay] = useState({ teams: true, capitals: true, lines: true, confCountry: true });
  const [confCountryOpacity, setConfCountryOpacity] = useState(0.1)


  const [conferenceNames, setConferenceNames] = useState([])
  const [selectedConference, setSelectedConference] = useState('')
  const [conferenceYears, setConferenceYears] = useState([])
  const [selectedYear, setSelectedYear] = useState('')
  const [sport, setSport] = useState('football')
  const [splitConference, setSplitConference] = useState(false)

  { /* API Calls */ }
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
      let colors = {};
      logoResponse.data.forEach((logo) => {
        logos[logo.name] = logo.logo;
        colors[logo.name] = logo.colors;
      });
      setConferenceLogos(logos);
      setConferenceColors(colors);

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

  { /* Chart Builder */ }
  useEffect(() => {
    const loadImages = async () => {
      const footballImg = new Image();
      footballImg.src = footballImage;
      footballImg.width = 15;
      footballImg.height = 15;
      await new Promise((resolve, reject) => {
        footballImg.onload = resolve;
        footballImg.onerror = reject;
      });

      const basketballImg = new Image();
      basketballImg.src = basketballImage;
      basketballImg.width = 15;
      basketballImg.height = 15;
      await new Promise((resolve, reject) => {
        basketballImg.onload = resolve;
        basketballImg.onerror = reject;
      });

      let selectedConferenceList = [];
      if (sport === 'football') {
        selectedConferenceList = conferenceList.filter((conference) =>
          conference.conference === selectedConference && conference.football);
      } else {
        selectedConferenceList = conferenceList.filter((conference) =>
          conference.conference === selectedConference && conference.basketball);
      }

      setChartData({
        labels: selectedConferenceList ? selectedConferenceList.map((conference) => conference.year) : [],
        datasets: [
          {
            label: 'Average Distance Between Schools',
            data: selectedConferenceList ? selectedConferenceList.map((conference) => conference.avgDistanceBetweenSchools) : [],
            pointStyle: selectedConferenceList ? selectedConferenceList.map((conference) =>
              conference.year === selectedYear ? sport === 'football' ? footballImg : basketballImg : false) : [],
            borderColor: conferenceColors[selectedConference] ? conferenceColors[selectedConference].main : '#000', // Default to black if undefined
          },
          {
            label: 'Average Distance from Center',
            data: selectedConferenceList ? selectedConferenceList.map((conference) => conference.avgDistanceFromCenter) : [],
            pointStyle: selectedConferenceList ? selectedConferenceList.map((conference) =>
              conference.year === selectedYear ? sport === 'football' ? footballImg : basketballImg : false) : [],
            borderColor: conferenceColors[selectedConference] ? conferenceColors[selectedConference].light : '#000', // Default to black if undefined
          },
        ],
      });
    };

    loadImages().catch(console.error);
  }, [conferenceList, selectedConference, sport, selectedYear]);

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

  const selectConferenceHandler = (e) => {
    setAnimate(false)
    const button = e.target.closest('button');
    const conferenceName = button.getAttribute('data-conf-name');
    setSelectedConference(conferenceName)
  }

  const selectYearHandler = (year) => {
    setSelectedYear(year)
  }

  const yearSearch = (e) => {
    let year = e.target.value;
    console.log(year)
    if (year.length == 4 && !isNaN(year) && year >= conferenceYears[0] && year <= conferenceYears[conferenceYears.length - 1]) {
      setSelectedYear(Number(year))
      setRedrawTimelineBool(true)
    }
  }

  const yearMapButtonHandler = (year) => {
    setSelectedYear(year)
    setRedrawTimelineBool(true)
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
    console.log(!animate)
    setAnimate(!animate)
  }

  useEffect(() => {
    let interval;
    if (animate) {
      let i = conferenceYears.indexOf(selectedYear) + 1;
      interval = setInterval(() => {
        if (i >= conferenceYears.length) {
          clearInterval(interval);
          setAnimate(false);
        } else {
          setSelectedYear(conferenceYears[i]);
          setRedrawTimelineBool(true);
          i++;
        }
      }, animationSpeed);
    }
    return () => clearInterval(interval);
  }, [animate, animationSpeed]);

  const autoScrollSpeedHandler = (value) => {
    const newSpeed = value === 'increase' ? Math.min(animationSpeed + 100, 1500) : Math.max(animationSpeed - 100, 100);
    setAnimationSpeed(newSpeed);
  }

  const handleMapDisplay = (value) => {
    switch (value) {
      case 'capitals':
        setMapDisplay({ teams: mapDisplay.teams, capitals: !mapDisplay.capitals, lines: mapDisplay.lines, confCountry: mapDisplay.confCountry });
        break;
      case 'teams':
        setMapDisplay({ teams: !mapDisplay.teams, capitals: mapDisplay.capitals, lines: mapDisplay.lines, confCountry: mapDisplay.confCountry });
        break;
      case 'lines':
        setMapDisplay({ teams: mapDisplay.teams, capitals: mapDisplay.capitals, lines: !mapDisplay.lines, confCountry: mapDisplay.confCountry });
        break;
      case 'confCountry':
        setMapDisplay({ teams: mapDisplay.teams, capitals: mapDisplay.capitals, lines: mapDisplay.lines, confCountry: !mapDisplay.confCountry });
        break;
      default:
        break;
    }
  };

  const handleConfCountryOpacity = (value) => {
    if (value === 'increase') {
      setConfCountryOpacity(parseFloat((Math.min(confCountryOpacity + 0.1, 1)).toFixed(1)));
    } else {
      setConfCountryOpacity(parseFloat((Math.max(confCountryOpacity - 0.1, 0.1)).toFixed(1)));
    }
  }

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
          {console.log({ conferenceColors })}
          <NavBar conferenceNames={conferenceNames}
            conferenceYears={conferenceYears}
            selectConference={selectConferenceHandler}
            searchYears={yearSearch}
            conferenceLogosObject={conferenceLogos}
            selectedYear={selectedYear}
            sportHandler={sportHandler}
            splitConference={splitConference} />
          <div className='row map-chart-row'>
            <div className='col-12 col-md-7'>
              <div className="map-container">
                <Map filteredConferenceList={filteredConferenceList}
                  conferenceIcons={conferenceIcons}
                  schoolIcons={schoolIcons}
                  selectedConference={selectedConference}
                  mapElements={mapDisplay}
                  confColors={conferenceColors} 
                  countryOpacity={confCountryOpacity}/>
                <DraggableTimeline
                  years={conferenceYears}
                  setYear={selectYearHandler}
                  selectedYear={selectedYear}
                  redraw={redrawTimelineBool}
                  setRedraw={setRedrawTimelineBool}
                  setAnimate={setAnimate} />
                <MapControls
                  setAnimation={animationHandler}
                  animate={animate} firstYear={conferenceYears[0]}
                  lastYear={conferenceYears[conferenceYears.length - 1]}
                  setYear={yearMapButtonHandler}
                  selectedConference={selectedConference}
                  setAutoScrollSpeed={autoScrollSpeedHandler}
                  setMapDisplayOptions={handleMapDisplay}
                  animationSpeed={animationSpeed}
                  mapDisplayOptions={mapDisplay} 
                  confCountryOpacity={confCountryOpacity}
                  setConfCountryOpacity={handleConfCountryOpacity}/>
              </div>
            </div>
            <div className='col-12 col-md-5'>
              <div className='chart-details-container'>
                <ConferenceDetails
                  conference={filteredConferenceList[0]}
                  confLogos={conferenceLogos}
                  confColors={conferenceColors}
                  selectedConference={selectedConference} />
                <div className='chart-container'>
                  <Line data={chartData} options={chartOptions} />
                </div>
                <ChartControls
                  setAnimation={animationHandler}
                  animate={animate}
                  firstYear={conferenceYears[0]}
                  lastYear={conferenceYears[conferenceYears.length - 1]}
                  setYear={yearMapButtonHandler} />
              </div>
            </div>
          </div>
        </>
      }
    </>
  )
}

function ChartControls({ setAnimation, animate, firstYear, lastYear, setYear }) {
  return (
    <nav className="navbar chart-controls" >
      <div className="container-fluid ">
        <div className="nav-item button-container">
          <button onClick={() => setYear(firstYear)} className='first-year-button'>
            {firstYear}
          </button>
          <button onClick={() => setYear(lastYear)} className='present-button'>
            {lastYear}
          </button>
        </div>
        <AutoScrollButton setAnimation={setAnimation} animate={animate} />
        <div className='nav-item map-controls-button secondary-button'>
          <button>...</button>
        </div>
      </div>
    </nav>
  )
};

function MapControls({ setAnimation, animate, firstYear, lastYear, setYear, selectedConference, setAutoScrollSpeed, setMapDisplayOptions, mapDisplayOptions, animationSpeed, confCountryOpacity, setConfCountryOpacity }) {
  return (
    <nav className="navbar map-controls">
      <div className="container-fluid">
        <li className="nav-item button-container">
          <button onClick={() => setYear(firstYear)} className='first-year-button'>
            {firstYear}
          </button>
          <button onClick={() => setYear(lastYear)} className='present-button'>
            {lastYear}
          </button>
        </li>
        <AutoScrollButton setAnimation={setAnimation} animate={animate} />
        <li className="nav-item dropdown more-circle">
          <a className="nav-link more-button more-button-container" href="#" id="navbarDropdown" role="button"
            data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">...</a>
          <ul className="dropdown-menu dropdown-menu-up more-map-menu" aria-labelledby="navbarDropdown">

            <h3 className='map-controls-header'>Map Controls</h3>

            <button className='btn btn-secondary map-more-control' onClick={(e) => { e.stopPropagation(); setMapDisplayOptions("confCountry"); }}>
              Show "{selectedConference} Country" {mapDisplayOptions.confCountry ? <span className='option-check'>&#10003;</span> : null}
            </button>

            <button value="capitalsonly" className='btn btn-secondary map-more-control' onClick={(e) => { e.stopPropagation(); setMapDisplayOptions("capitals"); }}>
              Show Capitals {mapDisplayOptions.capitals ? <span className='option-check'>&#10003;</span> : null}
            </button>

            <button value="teamsonly" className='btn btn-secondary map-more-control' onClick={(e) => { e.stopPropagation(); setMapDisplayOptions("teams"); }}>
              Show Teams {mapDisplayOptions.teams ? <span className='option-check'>&#10003;</span> : null}
            </button>

            <button value="both" className='btn btn-secondary map-more-control' onClick={(e) => { e.stopPropagation(); setMapDisplayOptions("lines"); }}>
              Show Lines to GeoCenter {mapDisplayOptions.lines ? <span className='option-check'>&#10003;</span> : null}
            </button>

            <div className='map-more-control'>
              <p>AutoScroll Speed</p>
              <div className='map-control-plusminus-container'>
                <button className='plusminus-btn' onClick={(e) => { e.stopPropagation(); setAutoScrollSpeed("increase"); }}>+</button>
                <button className='plusminus-btn' onClick={(e) => { e.stopPropagation(); setAutoScrollSpeed("decrease"); }}>-</button>
                <div className='plusminus-display'>{`${animationSpeed / 1000} s`}</div>
              </div>
            </div>

            <div className='map-more-control'>
              <p>Opacity</p>
              <div className='map-control-plusminus-container'>
                <button className='plusminus-btn' onClick={(e) => { e.stopPropagation(); setConfCountryOpacity("increase"); }}>+</button>
                <button className='plusminus-btn' onClick={(e) => { e.stopPropagation(); setConfCountryOpacity("decrease"); }}>-</button>
                <div className='plusminus-display'>{`${confCountryOpacity}`}</div>
              </div>
            </div>
                
          </ul>
        </li>

      </div>
    </nav>
  )
}

function AutoScrollButton({ setAnimation, animate }) {
  return (
    <button onClick={setAnimation} className='nav-item autoscroll-button'>
      <p>Autoscroll </p>
      {animate ? <img src={pauseImage} /> : <img src={playImage} />}
    </button>
  )
}

function NavBar({ conferenceNames, selectConference, searchYears, conferenceLogosObject, sportHandler }) {
  return (
    <>
      <nav className="navbar navbar-main navbar-expand-lg" >
        <div className="container-fluid">
          <a className="navbar-brand" href="#"> CFB Realignment Map</a >
          <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent"
            aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <img src="/images/menu.png" alt="hamburger" className='navbar-toggler-img' />
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
            </ul>
          </div>

          <ul className="navbar-nav d-flex flex-row me-1">
            <li className="nav-item me-3 me-lg-0">
              <a className="nav-link" href="https://github.com/EvanJelley/CFBRealignmentVisualizer" target="_blank" rel="noopener noreferrer">
                <img src={githubLogo} alt='GitHub' className='navbar-logo' />
              </a>
            </li>
          </ul>

          <form className="w-auto" onChange={searchYears} onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
            }
          }}>
            <input type="search" className="form-control searchbar" placeholder="Type a Year" aria-label="Search" maxLength="4" />
          </form>
        </div >
      </nav >
    </>
  )
}


const DraggableTimeline = ({ years, setYear, selectedYear, redraw, setRedraw, setAnimate }) => {

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
    if (redraw) {
      console.log('redraw')
      setDraggableKey(draggableKey + 1);
      setPrevYear(selectedYear);
      setYear(selectedYear);
      setPosition({ x: -(selectedYear - years[0]) * yearWidth - yearWidth / 2, y: 0, percentPosition: -(selectedYear - years[0]) / yearRange });
      setRedraw(false);
    }
  }, [redraw]);

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
  }, [lineDotRef.current, redraw]);

  const handleDrag = (e, data) => {
    setAnimate(false);
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
                    background: selectedYear == year ? '#00254c' : 'white',
                    color: selectedYear == year ? 'white' : '#00254c',
                    border: '1px solid #ccc',
                  }}
                  className='timeline-year'
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
        ></div>
      </div>
    </>
  );
};

function Map({ filteredConferenceList, conferenceIcons, schoolIcons, selectedConference, mapElements, confColors, countryOpacity }) {

  const mapRef = useRef(null);
  const containerRef = useRef(null);
  const [width, setwidth] = useState(window.innerWidth);
  const [schoolCoordinates, setSchoolCoordinates] = useState([]);
  const [schoolToCenterLines, setSchoolToCenterLines] = useState([])

  const CircleRadius = 200 * 1609

  useEffect(() => {
    let coords = [];
    let linesToCenter = [];
    filteredConferenceList.map((conference) => {
      conference.schools.map((school) => {
        coords.push([Number(school.latitude), Number(school.longitude)]);
        let lineToCenter = []
        lineToCenter.push([Number(school.latitude), Number(school.longitude)]);
        lineToCenter.push([Number(conference.capital.latitude), Number(conference.capital.longitude)]);
        linesToCenter.push(lineToCenter)
      });
    });
    console.log(linesToCenter)
    setSchoolCoordinates(coords);
    setSchoolToCenterLines(linesToCenter)
  }, [filteredConferenceList]);

  const calculateHeight = () => {
    if (width < 480) return 33;
    if (width < 1500) return 50;
    return 75;
  };

  const [mapHeight, setMapHeight] = useState(calculateHeight());


  const handleResize = () => {
    if (mapRef.current) {
      setwidth(window.innerWidth);
      const { current: map } = mapRef;
      map.fitBounds(USbounds);
      map.zoomControl.setPosition('topright');
    }
  };

  useEffect(() => {
    setMapHeight(calculateHeight());
  }, [width]);

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

  const USbounds = [
    [49.3457868, -66.93457],
    [24.396308, -125.0859375]
  ];

  const greaterUsBounds = [
    [51, -64],
    [22, -127]
  ];

  console.log(confColors[selectedConference])

  const lineOptions = { color: confColors[selectedConference].main, weight: "1", fill: true, }
  const circleOptions = { color: confColors[selectedConference].light, fillOpacity: countryOpacity, }


  return (
    <div ref={containerRef}>
      {console.log(mapHeight)}
      <MapContainer
        key={mapHeight}
        maxBounds={USbounds}
        maxBoundsViscosity={1.0}
        ref={mapRef}
        style={{ height: `${mapHeight}vh`, width: '100%' }}
        zoomSnap={.25}
        zoomDelta={.5}
        minZoom={2}
        maxZoom={5}
        whenCreated={(mapInstance) => { mapRef.current = mapInstance; handleResize(); }}
      >
        <TileLayer
          attribution='&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url='https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png'
        />

        {selectedConference == 'NCAA' && mapElements.teams ?
          filteredConferenceList.map((conference) => conference.schools.map((school) => (
            <>
              {mapElements.teams ?
                <Marker key={`${school.name}-${school.id}`} position={[Number(school.latitude), Number(school.longitude)]}
                  icon={conferenceIcons[conference.conference] || myIcon} zIndexOffset={1000}>
                  <Popup>
                    {school.name} - {school.city}, {school.state}
                  </Popup>
                </Marker>
                : null
              }
              {mapElements.confCountry ?
                <Circle
                  center={[Number(school.latitude), Number(school.longitude)]}
                  pathOptions={circleOptions}
                  radius={CircleRadius}
                  stroke={false} 
                  />
                : null
              }
            </>
          ))
          )
          :
          filteredConferenceList.map((conference) => conference.schools.map((school) => (
            <>
              {mapElements.teams ?
                <Marker key={`${school.name}-${school.id}`} position={[Number(school.latitude), Number(school.longitude)]}
                  icon={schoolIcons[school.name]} zIndexOffset={1000}>
                  <Popup>
                    {school.name} - {school.city}, {school.state}
                  </Popup>
                </Marker>
                : null
              }
              {mapElements.confCountry ?
                <Circle
                  center={[Number(school.latitude), Number(school.longitude)]}
                  pathOptions={circleOptions}
                  radius={CircleRadius}
                  stroke={false} 
                  />
                : null
              }
            </>
          ))
          )}
        {mapElements.capitals && filteredConferenceList.map((conference) => (
          <Marker key={`${conference.capital.name}-${conference.id}`}
            position={[Number(conference.capital.latitude), Number(conference.capital.longitude)]}
            icon={conferenceIcons[conference.conference]} zIndexOffset={500}>
            <Popup>
              Proposed {conference.conference} Capital: {conference.capital.name} - {conference.capital.state}
            </Popup>
          </Marker>
        ))}
        {filteredConferenceList.map((conference) => (conference.schools.map((school) => (
          school.name.includes('Hawai') && mapElements.teams ?
            <HawaiiMapOverlay school={school} schoolIcons={schoolIcons} conference={conference} lineOptions={lineOptions} />
            : null)
        )))}

        {mapElements.lines && <Polyline pathOptions={lineOptions} positions={schoolToCenterLines} />}
      </MapContainer>
    </div>
  )
};

const HawaiiMapOverlay = ({ school, schoolIcons, conference, lineOptions }) => {
  const hawaiiCenter = [20.7984, -157];

  const lineToCenter = [hawaiiCenter, [Number(conference.capital.latitude), Number(conference.capital.longitude)]]

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
      <Polyline pathOptions={lineOptions} positions={lineToCenter} />
    </MapContainer>
  );
};

function ConferenceDetails({ conference, confLogos, confColors, selectedConference }) {
  return (
    <div className='conference-details'>
      <div className='conference-details-main'>
        <h3 className='conference-details-conference'>
          <span className='conference-details-category-header'>Conference:</span>
          <img className='conference-details-conference-img' src={confLogos[conference.conference]} />
        </h3>
        <h3 className='conference-details-year'>
          <span className='conference-details-category-header'>
            Year:
          </span>
          <span className='conference-details-category-header-year'>
            {conference.year}
          </span>
        </h3>
      </div>
      <div className='conference-details-specific'>
        <table className='conference-details-table'>
          <tbody>
            <tr>
              <td className='conference-details-category'>Proposed Capital</td>
              <td className='conference-details-item'>{conference.capital.name}, {conference.capital.state}</td>
            </tr>
            <tr>
              <td className='conference-details-category'>Number of Schools</td>
              <td className='conference-details-item'>{conference.schools.length}</td>
            </tr>
            <tr>
              <td className='conference-details-category'>
                <span className="conference-details-color-square" style={{ backgroundColor: confColors[selectedConference].main }}></span>
                Avg. Distance Between Schools
              </td>
              <td className='conference-details-item'>{Math.round(conference.avgDistanceBetweenSchools)} miles</td>
            </tr>
            <tr>
              <td className='conference-details-category'>
                <span className="conference-details-color-square" style={{ backgroundColor: confColors[selectedConference].light }}></span>
                Avg. Distance from GeoCenter
              </td>
              <td className='conference-details-item'>{Math.round(conference.avgDistanceFromCenter)} miles</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
};

export default App