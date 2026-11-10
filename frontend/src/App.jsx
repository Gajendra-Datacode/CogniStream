
import { useEffect, useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts'
import './App.css'

function App() {
  // Dashboard states
  const [developers, setDevelopers] = useState([])
  const [flowData, setFlowData] = useState([])
  const [cognitiveData, setCognitiveData] = useState([])
  const [contextData, setContextData] = useState([])

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Developer filter
  const [selectedDeveloper, setSelectedDeveloper] = useState('All')

  // Fetch dashboard data from FastAPI
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true)
        setError('')

        const [
          developerResponse,
          flowResponse,
          cognitiveResponse,
          contextResponse
        ] = await Promise.all([
          fetch('/api/developers'),
          fetch('/api/flow-sessions'),
          fetch('/api/cognitive-load'),
          fetch('/api/context-switching')
        ])

        if (
          !developerResponse.ok ||
          !flowResponse.ok ||
          !cognitiveResponse.ok ||
          !contextResponse.ok
        ) {
          throw new Error(
            'Unable to fetch dashboard data from FastAPI'
          )
        }

        const developerResult = await developerResponse.json()
        const flowResult = await flowResponse.json()
        const cognitiveResult = await cognitiveResponse.json()
        const contextResult = await contextResponse.json()

        setDevelopers(
          Array.isArray(developerResult) ? developerResult : []
        )

        setFlowData(
          Array.isArray(flowResult)
            ? flowResult
            : flowResult.flow_sessions || []
        )

        setCognitiveData(
          Array.isArray(cognitiveResult)
            ? cognitiveResult
            : cognitiveResult.cognitive_load || []
        )

        setContextData(
          Array.isArray(contextResult) ? contextResult : []
        )

      } catch (err) {
        setError(err.message || 'Something went wrong')
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  // Get all unique developer IDs
  const developerOptions = [
    ...new Set([
      ...developers.map(item => item.developer_id),
      ...flowData.map(item => item.developer_id),
      ...cognitiveData.map(item => item.developer_id),
      ...contextData.map(item => item.developer_id)
    ].filter(Boolean))
  ].sort()

  // Filter data according to selected developer
  const filterByDeveloper = (data) => {
    if (selectedDeveloper === 'All') {
      return data
    }

    return data.filter(
      item => item.developer_id === selectedDeveloper
    )
  }

  const filteredDevelopers = filterByDeveloper(developers)
  const filteredFlowData = filterByDeveloper(flowData)
  const filteredCognitiveData = filterByDeveloper(cognitiveData)
  const filteredContextData = filterByDeveloper(contextData)

  // Developer calculations
  const totalDevelopers = filteredDevelopers.length

  const totalEvents = filteredDevelopers.reduce(
    (total, developer) =>
      total + Number(developer.total_events || 0),
    0
  )

  // Flow-state calculations
  const totalSessions = filteredFlowData.length

  const deepFocusSessions = filteredFlowData.filter(
    session =>
      session.qualified_90_min === true ||
      session.qualified_90_min === 1
  )

  const longestSession = filteredFlowData.reduce(
    (longest, session) =>
      Math.max(
        longest,
        Number(session.duration_minutes || 0)
      ),
    0
  )

  const averageDuration = totalSessions
    ? (
        filteredFlowData.reduce(
          (total, session) =>
            total + Number(session.duration_minutes || 0),
          0
        ) / totalSessions
      ).toFixed(1)
    : '0.0'

  // Cognitive load calculations
  const averageFocus = filteredCognitiveData.length
    ? (
        filteredCognitiveData.reduce(
          (total, item) =>
            total + Number(item.focus_percentage || 0),
          0
        ) / filteredCognitiveData.length
      ).toFixed(1)
    : '0.0'

  const averageInterruption = filteredCognitiveData.length
    ? (
        filteredCognitiveData.reduce(
          (total, item) =>
            total + Number(item.interruption_percentage || 0),
          0
        ) / filteredCognitiveData.length
      ).toFixed(1)
    : '0.0'

  // Context switching calculations
  const totalInterruptions = filteredContextData.reduce(
    (total, item) =>
      total + Number(item.total_interruptions || 0),
    0
  )

  const totalSwitches = filteredContextData.reduce(
    (total, item) =>
      total + Number(item.focus_to_interruption_switches || 0),
    0
  )

  return (
    <div className="dashboard">

      {/* Sidebar */}
      <aside className="sidebar">

        <h2>🧠 CogniStream</h2>

        <p className="menu-title">WORKSPACE</p>

        <a href="#overview" className="active">
          ▦ Overview
        </a>

        <a href="#developer-analytics">
          ◉ Developer Analytics
        </a>

        <a href="#flow-state">
          ⌁ Flow State
        </a>

        <a href="#cognitive-load">
          ◷ Cognitive Load
        </a>

        <a href="#context-switching">
          ⇄ Context Switching
        </a>

        <a href="#summary">
          Project Summary
        </a>

        <p className="menu-title">SYSTEM</p>

        <a href="#system-status">
          ⚙ System Status
        </a>

      </aside>

      {/* Main Content */}
      <main className="main-content" id="overview">

        {/* Header */}
        <header>

          <div>
            <h1>Developer Analytics Dashboard</h1>

            <p>
              Monitor developer activity, focus sessions
              and cognitive load.
            </p>
          </div>

          <span className="status" id="system-status">
            ● {error ? 'Connection Error' : 'System Online'}
          </span>

        </header>

        {/* Developer Filter */}
        <section
          className="panel"
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '15px'
          }}
        >

          <div>
            <h2>Dashboard Filters</h2>

            <p className="section-description">
              Select a developer to view individual analytics.
            </p>
          </div>

          <div>
            <label
              htmlFor="developer-filter"
              style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '600'
              }}
            >
              Select Developer
            </label>

            <select
              id="developer-filter"
              value={selectedDeveloper}
              onChange={(event) =>
                setSelectedDeveloper(event.target.value)
              }
              style={{
                padding: '10px 15px',
                minWidth: '190px',
                borderRadius: '8px',
                border: '1px solid #64748b',
                background: '#ffffff',
                color: '#111827',
                fontSize: '14px',
                cursor: 'pointer'
              }}
            >

              <option value="All">
                All Developers
              </option>

              {developerOptions.map(developer => (
                <option key={developer} value={developer}>
                  {developer}
                </option>
              ))}

            </select>
          </div>

        </section>

        {/* API Error */}
        {error && (
          <div className="error-message">
            <strong>API Error:</strong> {error}

            <p>
              Check that your FastAPI server is running.
            </p>
          </div>
        )}

        {/* KPI Cards */}
        <section className="cards">

          <div className="card">
            <p>Total Developers</p>

            <h2>
              {loading ? '...' : totalDevelopers}
            </h2>

            <small>
              {selectedDeveloper === 'All'
                ? 'All developers'
                : 'Selected developer'}
            </small>
          </div>

          <div className="card">
            <p>Total Activity Events</p>

            <h2>
              {loading ? '...' : totalEvents}
            </h2>

            <small>Recorded events</small>
          </div>

          <div className="card">
            <p>Deep Focus Sessions</p>

            <h2>
              {loading ? '...' : deepFocusSessions.length}
            </h2>

            <small>Sessions of 90+ minutes</small>
          </div>

          <div className="card">
            <p>Longest Focus Session</p>

            <h2>
              {loading ? '...' : `${longestSession} min`}
            </h2>

            <small>Maximum session duration</small>
          </div>

        </section>

        {/* Developer Analytics */}
        <section className="panel" id="developer-analytics">

          <h2>Developer Activity</h2>

          <p className="section-description">
            Activity records received from the FastAPI backend.
          </p>

          {loading ? (
            <p>Loading developer data...</p>
          ) : filteredDevelopers.length === 0 ? (
            <p>No developer records found.</p>
          ) : (

            <div className="table-container">

              <table>

                <thead>
                  <tr>
                    <th>Developer ID</th>
                    <th>Total Events</th>
                  </tr>
                </thead>

                <tbody>
                  {filteredDevelopers.map(developer => (
                    <tr key={developer.developer_id}>
                      <td>{developer.developer_id}</td>
                      <td>{developer.total_events}</td>
                    </tr>
                  ))}
                </tbody>

              </table>

            </div>
          )}

        </section>

        {/* Flow-State Analytics */}
        <section className="panel" id="flow-state">

          <h2>Flow-State Analytics</h2>

          <p className="section-description">
            Analyze developer focus sessions and session duration.
          </p>

          <div className="flow-summary">

            <div>
              <span>Total Sessions</span>

              <h3>
                {loading ? '...' : totalSessions}
              </h3>
            </div>

            <div>
              <span>Average Duration</span>

              <h3>
                {loading ? '...' : `${averageDuration} min`}
              </h3>
            </div>

            <div>
              <span>Deep Focus Sessions</span>

              <h3>
                {loading ? '...' : deepFocusSessions.length}
              </h3>
            </div>

          </div>

          {loading ? (
            <p>Loading flow-state data...</p>
          ) : filteredFlowData.length === 0 ? (
            <p>No flow-state sessions found.</p>
          ) : (

            <div className="table-container">

              <table>

                <thead>
                  <tr>
                    <th>Developer</th>
                    <th>Duration</th>
                    <th>Focus Events</th>
                    <th>90+ Minutes</th>
                  </tr>
                </thead>

                <tbody>
                  {filteredFlowData.map((session, index) => (

                    <tr key={`${session.developer_id}-${index}`}>

                      <td>{session.developer_id}</td>

                      <td>
                        {session.duration_minutes} min
                      </td>

                      <td>{session.focus_events}</td>

                      <td>
                        {session.qualified_90_min ? (
                          <span className="success">Yes</span>
                        ) : (
                          <span className="muted">No</span>
                        )}
                      </td>

                    </tr>

                  ))}
                </tbody>

              </table>

            </div>
          )}

        </section>

        {/* Cognitive Load Analytics */}
        <section className="panel" id="cognitive-load">

          <h2>Cognitive Load Analytics</h2>

          <p className="section-description">
            Analyze event-based focus and interruption indicators
            for developers.
          </p>

          <div className="flow-summary">

            <div>
              <span>Average Focus</span>

              <h3>
                {loading ? '...' : `${averageFocus}%`}
              </h3>
            </div>

            <div>
              <span>Average Interruptions</span>

              <h3>
                {loading ? '...' : `${averageInterruption}%`}
              </h3>
            </div>

            <div>
              <span>Developers Analyzed</span>

              <h3>
                {loading ? '...' : filteredCognitiveData.length}
              </h3>
            </div>

          </div>

          {/* Cognitive Load Table */}
          {loading ? (
            <p>Loading cognitive load data...</p>
          ) : filteredCognitiveData.length === 0 ? (
            <p>No cognitive load records found.</p>
          ) : (

            <div className="table-container">

              <table>

                <thead>
                  <tr>
                    <th>Developer</th>
                    <th>Focus Events</th>
                    <th>Interruption Events</th>
                    <th>Focus %</th>
                    <th>Interruption %</th>
                  </tr>
                </thead>

                <tbody>
                  {filteredCognitiveData.map((item, index) => (

                    <tr key={`${item.developer_id}-${index}`}>

                      <td>{item.developer_id}</td>
                      <td>{item.focus_events}</td>
                      <td>{item.interruption_events}</td>
                      <td>{item.focus_percentage}%</td>
                      <td>{item.interruption_percentage}%</td>

                    </tr>

                  ))}
                </tbody>

              </table>

            </div>
          )}

          {/* Cognitive Load Chart */}
          <div className="chart-container">

            <h3>Developer Focus vs Interruption (%)</h3>

            {loading ? (
              <p>Loading chart data...</p>
            ) : filteredCognitiveData.length === 0 ? (
              <p>No chart data available.</p>
            ) : (

              <ResponsiveContainer width="100%" height={320}>

                <BarChart
                  data={filteredCognitiveData}
                  margin={{
                    top: 20,
                    right: 20,
                    left: 10,
                    bottom: 10
                  }}
                >

                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis dataKey="developer_id" />

                  <YAxis domain={[0, 100]} />

                  <Tooltip />

                  <Legend />

                  <Bar
                    dataKey="focus_percentage"
                    name="Focus Percentage"
                    fill="#38bdf8"
                    radius={[5, 5, 0, 0]}
                  />

                  <Bar
                    dataKey="interruption_percentage"
                    name="Interruption Percentage"
                    fill="#a78bfa"
                    radius={[5, 5, 0, 0]}
                  />

                </BarChart>

              </ResponsiveContainer>
            )}

          </div>

          <p className="section-description">
            These percentages are estimates based on simulated
            activity events, not direct measurements of mental workload.
          </p>

        </section>

        {/* Context Switching Analytics */}
        <section className="panel" id="context-switching">

          <h2>Context Switching Analytics</h2>

          <p className="section-description">
            Analyze developer interruptions and
            focus-to-interruption transitions.
          </p>

          <div className="flow-summary">

            <div>
              <span>Total Interruptions</span>

              <h3>
                {loading ? '...' : totalInterruptions}
              </h3>
            </div>

            <div>
              <span>Focus-to-Interruption Switches</span>

              <h3>
                {loading ? '...' : totalSwitches}
              </h3>
            </div>

            <div>
              <span>Developers Analyzed</span>

              <h3>
                {loading ? '...' : filteredContextData.length}
              </h3>
            </div>

          </div>

          {/* Context Switching Chart */}
          <div className="chart-container">

            <h3>Developer Interruption Comparison</h3>

            {loading ? (
              <p>Loading chart data...</p>
            ) : filteredContextData.length === 0 ? (
              <p>No chart data available.</p>
            ) : (

              <ResponsiveContainer width="100%" height={320}>

                <BarChart
                  data={filteredContextData}
                  margin={{
                    top: 20,
                    right: 20,
                    left: 10,
                    bottom: 10
                  }}
                >

                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis dataKey="developer_id" />

                  <YAxis allowDecimals={false} />

                  <Tooltip />

                  <Legend />

                  <Bar
                    dataKey="total_interruptions"
                    name="Total Interruptions"
                    fill="#38bdf8"
                    radius={[5, 5, 0, 0]}
                  />

                  <Bar
                    dataKey="focus_to_interruption_switches"
                    name="Focus Switches"
                    fill="#a78bfa"
                    radius={[5, 5, 0, 0]}
                  />

                </BarChart>

              </ResponsiveContainer>
            )}

          </div>

          {/* Context Switching Table */}
          {loading ? (
            <p>Loading context switching data...</p>
          ) : filteredContextData.length === 0 ? (
            <p>No context switching records found.</p>
          ) : (

            <div className="table-container">

              <table>

                <thead>
                  <tr>
                    <th>Developer</th>
                    <th>Total Interruptions</th>
                    <th>Focus-to-Interruption Switches</th>
                  </tr>
                </thead>

                <tbody>
                  {filteredContextData.map(item => (

                    <tr key={item.developer_id}>

                      <td>{item.developer_id}</td>

                      <td>{item.total_interruptions}</td>

                      <td>
                        {item.focus_to_interruption_switches}
                      </td>

                    </tr>

                  ))}
                </tbody>

              </table>

            </div>
          )}

          <p className="section-description">
            Context switching metrics are calculated from
            simulated developer activity events.
          </p>

        </section>

        {/* Project Summary */}
        <section className="panel" id="summary">

          <h2>Project Summary</h2>

          <p>
            CogniStream analyzes simulated developer activity
            to identify focus sessions, interruptions,
            context switching and activity patterns.
          </p>

          <p className="section-description">
            Analytics are based on simulated event data and are
            not direct measurements of actual productivity
            or cognitive load.
          </p>

        </section>

        {/* Footer */}
        <footer>
          CogniStream © 2026 |
          Developer Flow-State & Cognitive Load Analytics
        </footer>

      </main>

    </div>
  )
}

export default App
