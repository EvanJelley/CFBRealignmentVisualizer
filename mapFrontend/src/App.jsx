import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import axios from 'axios'




function App() {

  const [conferenceList, setConferenceList] = useState([])
  const [filteredConferenceList, setFilteredConferenceList] = useState([])

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
      console.log('All Conferences')
      let filteredList = conferenceList.filter((conference) => {
        return conference.year == selectedYear
      })
      setFilteredConferenceList(filteredList)
    } else {
      console.log('Specific Conference')
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
      console.log(selectedYear, years)
    } else {
      console.log('Specific Conference')
      let years = []
      conferenceList.map((conference) => {
        conference.conference == selectedConference && !years.includes(conference.year) ? years.push(conference.year) : null
      });
      years.sort()
      setConferenceYears(years)
      console.log(selectedYear, years)
      years.includes(selectedYear) ? conferenceFilter() : setSelectedYear(years[0])
    }
  }, [selectedConference])


  return (
    <>
      <h1>Conference Realignment Map</h1>
      <OptionBay conferenceNames={conferenceNames} conferenceYears={conferenceYears} selectConference={selectConferenceHandler} selectYear={selectYearHandler} />
      <ul>
        {filteredConferenceList.map((conference) => (
          <li key={conference.id}>
            {conference.conference} - {conference.year}
            <ul>
              {conference.schools.map((school) => (
                <li key={school.id}>
                  {school.name} - {school.city}, {school.state} - {school.latitude.toFixed(3)}, {school.longitude.toFixed(3)}
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
      <Map conferenceList={filteredConferenceList} />
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

function Map ({ conferenceList }) {
  return (
    <div>
      <h1>Map</h1>
    </div>
  )
}

export default App
