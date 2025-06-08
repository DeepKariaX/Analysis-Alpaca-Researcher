import React from 'react';

const Header = () => {
  return (
    <header style={{
      background: 'rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(10px)',
      padding: '1rem 2rem',
      borderBottom: '1px solid rgba(255, 255, 255, 0.2)'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div>
          <h1 style={{
            color: 'white',
            fontSize: '1.8rem',
            fontWeight: '700',
            margin: 0
          }}>
            🦙 AnalysisAlpaca
          </h1>
          <p style={{
            color: 'rgba(255, 255, 255, 0.8)',
            margin: '0.25rem 0 0 0',
            fontSize: '0.9rem'
          }}>
            AI-Powered Research & Analysis Platform
          </p>
        </div>
        
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem'
        }}>
          <div style={{
            background: 'rgba(255, 255, 255, 0.2)',
            padding: '0.5rem 1rem',
            borderRadius: '20px',
            fontSize: '0.8rem',
            color: 'white'
          }}>
            Powered by 🩶
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;