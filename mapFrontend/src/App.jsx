import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import axios from 'axios'




function App() {

  const [conferenceList, setConferenceList] = useState([])
  const [filteredConferenceList, setFilteredConferenceList] = useState([])
  const [conferenceNames, setConferenceNames] = useState([])

  const getConferences = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/conferencebyyear/')
      setConferenceList(response.data)
      setFilteredConferenceList(response.data)

      let conferenceNameList = []
      response.data.map((conference) => {
        conferenceNameList.includes(conference.conference) ? null :
        conferenceNameList.push(conference.conference)
      });
      setConferenceNames(conferenceNameList)
    } catch (error) {
      console.error(error)
    }
  }

  useEffect(() => {
    getConferences()
  }, [])

  let conferenceFilterHandler = (e) => {
    let filteredList = conferenceList.filter((conference) => {
      return conference.conference === e.target.value
    })
    setFilteredConferenceList(filteredList)
  }

  return (
    <>
      <h1>Conference Realignment Map</h1>
      <OptionBay conferenceNames={conferenceNames} conferenceFilterHandler={conferenceFilterHandler}/>
      <ul>
        {filteredConferenceList.map((conference) => (
          <li>
            {conference.conference} - {conference.year}
            <ul>
              {conference.schools.map((school) => (
                <li>
                  {school.name} - {school.city}, {school.state}
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </>
  )
}

function OptionBay({ conferenceNames, conferenceFilterHandler }) {
  return (
    <>
      <h3>Option Bay</h3>
      <select onChange={conferenceFilterHandler}>
        {conferenceNames.map((conferenceName) => (
          <option key={conferenceName}>{conferenceName}</option>
        ))}
      </select>
    </>
  )
}

export default App
