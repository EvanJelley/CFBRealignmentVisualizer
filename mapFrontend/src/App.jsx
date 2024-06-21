import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
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



function App() {

  const [conferenceList, setConferenceList] = useState([])
  const [filteredConferenceList, setFilteredConferenceList] = useState([])
  const [conferenceIcons, setConferenceIcons] = useState({})

  const [conferenceNames, setConferenceNames] = useState([])
  const [selectedConference, setSelectedConference] = useState('')
  const [conferenceYears, setConferenceYears] = useState([])
  const [selectedYear, setSelectedYear] = useState('')


  const getConferences = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/conferencebyyear/')
      setConferenceList(response.data)

      let conferenceNameList = []
      response.data.map((conference) => {
        conferenceNameList.includes(conference.conference) ? null :
          conferenceNameList.push(conference.conference)
      });
      conferenceNameList.push('All Conferences')
      setConferenceNames(conferenceNameList)

      let conferenceYearList = []
      response.data.map((conference) => {
        conferenceYearList.includes(conference.year) ? null :
          conferenceYearList.push(conference.year)
      });
      conferenceYearList.sort()
      setConferenceYears(conferenceYearList)

      setSelectedConference(conferenceNameList[0])
      const logoResponse = await axios.get('http://localhost:8000/api/conferencelogos/')
      let icons = {};
      logoResponse.data.forEach((logo) => {
        icons[logo.name] = L.icon({
          iconUrl: logo.logo,
          iconSize: [40,],
        });
      });
      setConferenceIcons(icons);
    } catch (error) {
      console.error(error)
    }
  }

  useEffect(() => {
    getConferences()
  }, [])

  let selectConferenceHandler = (e) => {
    setSelectedConference(e.target.value)
  }

  let selectYearHandler = (e) => {
    setSelectedYear(e.target.value)
  }

  let conferenceFilter = () => {
    if (selectedConference == 'All Conferences') {
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
    if (selectedConference == 'All Conferences') {
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
    iconUrl: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Big_12_Conference_logo.svg/1200px-Big_12_Conference_logo.svg.png',
    iconSize: [40, 40],
    iconAnchor: [20, 40],
    popupAnchor: [0, -40],
  });

  const usaBounds = [
    [5.499550, -167.276413],
    [83.162102, -52.233040]
  ];

  return (
    <>
      <div className='container'>
        <h1>Conference Realignment Map</h1>
        <div className='row'>
          {filteredConferenceList.length == 0 ?
            <p>Loading...</p>
            :
            <div className='col-12'>
              <OptionBay conferenceNames={conferenceNames} conferenceYears={conferenceYears} selectConference={selectConferenceHandler} selectYear={selectYearHandler} />
              <MapContainer style={{ height: "24rem", width: "100%" }} center={[37.0902, -95.7129]} zoom={4} 
              scrollWheelZoom={false} maxBounds={usaBounds} dragging={false} zoomControl={false}>
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {selectedConference == 'All Conferences' ?
                  filteredConferenceList.map((conference) =>
                    conference.schools.map((school) => (
                      <Marker key={school.id} position={[Number(school.latitude), Number(school.longitude)]} 
                      icon={conferenceIcons[selectedConference] || myIcon}>
                        <Popup>
                          {school.name} - {school.city}, {school.state}
                        </Popup>
                      </Marker>
                    ))
                  )
                  :
                  filteredConferenceList.map((conference) =>
                    conference.schools.map((school) => (
                      <Marker key={school.id} position={[Number(school.latitude), Number(school.longitude)]} 
                      icon={conferenceIcons[selectedConference] || myIcon}>
                        <Popup>
                          {school.name} - {school.city}, {school.state}
                        </Popup>
                      </Marker>
                    ))
                  )}
                {filteredConferenceList.map((conference) => (
                  <Marker key={conference.capital.id} position={[Number(conference.capital.latitude), Number(conference.capital.longitude)]}>
                    <Popup>
                      Proposed {conference.conference} Capital: {conference.capital.name} - {conference.capital.state}
                    </Popup>
                  </Marker>
                ))}
              </MapContainer>
            </div>
          }
        </div>
      </div>
      <ul>
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
      </ul>
    </>
  )
}

function OptionBay({ conferenceNames, conferenceYears, selectConference, selectYear }) {
  return (
    <>
      <h3>Option Bay</h3>
      <select onChange={selectConference}>
        {conferenceNames.map((conferenceName) => (
          <option key={conferenceName}>{conferenceName}</option>
        ))}
      </select>
      <select onChange={selectYear}>
        {conferenceYears.map((conferenceYear) => (
          <option key={conferenceYear}>{conferenceYear}</option>
        ))}
      </select>
    </>
  )
}

function Map({ conferenceList }) {
  let map = L.map('map').setView([51.505, -0.09], 13);
  return (
    <div>
      <h1>Map</h1>
    </div>
  )
}

export default App
