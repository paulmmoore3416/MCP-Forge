export default function Home() {
  return (
    <div style={{ 
      minHeight: '100vh',
      backgroundColor: 'var(--background-primary)',
      color: 'var(--text-primary)',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
    }}>
      {/* Header */}
      <header style={{
        borderBottom: '1px solid var(--border)',
        padding: '1rem 2rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600, margin: 0 }}>
            🔨 MCP Forge
          </h1>
          <span style={{ 
            fontSize: '0.75rem',
            padding: '0.25rem 0.5rem',
            backgroundColor: 'var(--accent)',
            color: 'white',
            borderRadius: '9999px',
            fontWeight: 500
          }}>
            v1.0.0
          </span>
        </div>
        <nav style={{ display: 'flex', gap: '1.5rem' }}>
          <a href="#" style={{ color: 'var(--text-primary)', textDecoration: 'none' }}>Dashboard</a>
          <a href="#" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Servers</a>
          <a href="#" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Monitoring</a>
          <a href="#" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Settings</a>
        </nav>
      </header>

      {/* Main Content */}
      <main style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
        {/* Hero Section */}
        <section style={{ textAlign: 'center', padding: '4rem 0' }}>
          <h2 style={{ 
            fontSize: '3rem', 
            fontWeight: 700, 
            marginBottom: '1rem',
            background: 'linear-gradient(135deg, var(--accent) 0%, var(--success) 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            Enterprise MCP Governance Platform
          </h2>
          <p style={{ 
            fontSize: '1.25rem', 
            color: 'var(--text-secondary)',
            maxWidth: '800px',
            margin: '0 auto 2rem'
          }}>
            Discover, manage, and monitor all your Model Context Protocol servers with 
            AI-powered security, real-time observability, and developer-first tools.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <button className="github-button" style={{ cursor: 'pointer' }}>
              Get Started
            </button>
            <button className="github-button-secondary" style={{ cursor: 'pointer' }}>
              View Documentation
            </button>
          </div>
        </section>

        {/* Stats Grid */}
        <section style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1.5rem',
          marginBottom: '3rem'
        }}>
          <div className="github-card">
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🔍</div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Auto-Discovery
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              Automatically scan and catalog MCP servers across your infrastructure
            </p>
          </div>

          <div className="github-card">
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🛡️</div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Security First
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              ML-powered anomaly detection and real-time security scanning
            </p>
          </div>

          <div className="github-card">
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>📊</div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Real-Time Monitoring
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              Sub-10ms latency tracking with comprehensive observability
            </p>
          </div>

          <div className="github-card">
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🛠️</div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Developer Tools
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              Integrated builder, testing sandbox, and code generation
            </p>
          </div>
        </section>

        {/* Status Section */}
        <section className="github-card" style={{ marginBottom: '3rem' }}>
          <h3 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1.5rem' }}>
            System Status
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Backend API</span>
              <span className="status-badge status-healthy">● Healthy</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Database</span>
              <span className="status-badge status-healthy">● Connected</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Redis Cache</span>
              <span className="status-badge status-healthy">● Active</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Monitoring</span>
              <span className="status-badge status-healthy">● Operational</span>
            </div>
          </div>
        </section>

        {/* Quick Links */}
        <section className="github-card">
          <h3 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1.5rem' }}>
            Quick Links
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <a href="http://localhost:8765/api/docs" target="_blank" rel="noopener noreferrer" 
               style={{ 
                 color: 'var(--accent)', 
                 textDecoration: 'none',
                 display: 'flex',
                 alignItems: 'center',
                 gap: '0.5rem'
               }}>
              📚 API Documentation →
            </a>
            <a href="http://localhost:9091" target="_blank" rel="noopener noreferrer"
               style={{ 
                 color: 'var(--accent)', 
                 textDecoration: 'none',
                 display: 'flex',
                 alignItems: 'center',
                 gap: '0.5rem'
               }}>
              📈 Prometheus Metrics →
            </a>
            <a href="http://localhost:3002" target="_blank" rel="noopener noreferrer"
               style={{ 
                 color: 'var(--accent)', 
                 textDecoration: 'none',
                 display: 'flex',
                 alignItems: 'center',
                 gap: '0.5rem'
               }}>
              📊 Grafana Dashboards →
            </a>
            <a href="https://github.com/paulmmoore3416/MCP-Forge" target="_blank" rel="noopener noreferrer"
               style={{ 
                 color: 'var(--accent)', 
                 textDecoration: 'none',
                 display: 'flex',
                 alignItems: 'center',
                 gap: '0.5rem'
               }}>
              💻 GitHub Repository →
            </a>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border)',
        padding: '2rem',
        textAlign: 'center',
        color: 'var(--text-secondary)',
        fontSize: '0.875rem',
        marginTop: '4rem'
      }}>
        <p>MCP Forge v1.0.0 - Phase 1 Complete</p>
        <p style={{ marginTop: '0.5rem' }}>
          Built with ❤️ for the MCP Community | 
          <a href="https://github.com/paulmmoore3416/MCP-Forge" 
             style={{ color: 'var(--accent)', marginLeft: '0.5rem' }}>
            GitHub
          </a>
        </p>
      </footer>
    </div>
  );
}