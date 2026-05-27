import { useWebSocket } from './hooks/useWebSocket';
import { useStats } from './hooks/useStats';
import { LiveGraph } from './components/LiveGraph';
import { ModelProviders } from './components/ModelProviders';
import './App.css';

const API_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws/events';

function App() {
  const { events, isConnected, lastEvent, clearEvents } = useWebSocket(WS_URL);
  const { stats, loading, error } = useStats(API_URL);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Schitzo Neural Router Dashboard</h1>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '● Connected' : '○ Disconnected'}
          </span>
        </div>
      </header>

      <main className="App-main">
        <section className="stats-section">
          <h2>Statistics</h2>
          {loading ? (
            <p>Loading stats...</p>
          ) : error ? (
            <p>Error: {error}</p>
          ) : stats ? (
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Total Requests</h3>
                <p>{stats.total_requests}</p>
              </div>
              <div className="stat-card">
                <h3>Today</h3>
                <p>{stats.requests_today}</p>
              </div>
              <div className="stat-card">
                <h3>Cost Today</h3>
                <p>${stats.cost_today_usd.toFixed(4)}</p>
              </div>
              <div className="stat-card">
                <h3>Events</h3>
                <p>{events.length}</p>
              </div>
            </div>
          ) : null}
        </section>

        <section className="live-section">
          <h2>Live Pipeline</h2>
          <LiveGraph events={events} lastEvent={lastEvent} />
        </section>

        <section className="events-section">
          <h2>
            Recent Events
            <button onClick={clearEvents} style={{ marginLeft: '12px', fontSize: '12px', padding: '4px 8px', cursor: 'pointer' }}>
              Clear
            </button>
          </h2>
          <div className="events-list">
            {events.slice(-10).reverse().map((event, index) => (
              <div key={index} className="event-item">
                <span className="event-type">{event.event_type}</span>
                <span className="event-time">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
                <span className="event-data">
                  {JSON.stringify(event.data, null, 0)}
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="providers-section">
          <h2>Model Providers</h2>
          <ModelProviders apiUrl={API_URL} />
        </section>
      </main>
    </div>
  );
}

export default App;
