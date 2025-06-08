import React, { useState, useEffect } from 'react';
import './App.css';
import ResearchForm from './components/ResearchForm';
import ResearchResults from './components/ResearchResults';
import JobsList from './components/JobsList';
import Header from './components/Header';
import { researchAPI } from './services/api';

function App() {
  const [currentJob, setCurrentJob] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [activeTab, setActiveTab] = useState('research');

  const handleNewResearch = async (researchData) => {
    try {
      const job = await researchAPI.startResearch(researchData);
      console.log('New research started:', job);
      setCurrentJob(job);
      setActiveTab('results');
      
      // Force refresh the jobs list after a short delay to ensure job appears
      setTimeout(() => {
        loadJobs();
      }, 500);
    } catch (error) {
      console.error('Failed to start research:', error);
      alert('Failed to start research. Please try again.');
    }
  };

  const handleSelectJob = (job) => {
    setCurrentJob(job);
    setActiveTab('results');
  };

  const loadJobs = async () => {
    try {
      const response = await researchAPI.listJobs();
      setJobs(response.jobs || []);
    } catch (error) {
      console.error('Failed to load jobs:', error);
    }
  };

  useEffect(() => {
    loadJobs();
    // Refresh jobs list every 30 seconds
    const interval = setInterval(loadJobs, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <Header />
      
      <nav className="tab-navigation">
        <button 
          className={`tab ${activeTab === 'research' ? 'active' : ''}`}
          onClick={() => setActiveTab('research')}
        >
          New Research
        </button>
        <button 
          className={`tab ${activeTab === 'results' ? 'active' : ''}`}
          onClick={() => setActiveTab('results')}
        >
          Current Research
        </button>
        <button 
          className={`tab ${activeTab === 'jobs' ? 'active' : ''}`}
          onClick={() => setActiveTab('jobs')}
        >
          Research History
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'research' && (
          <ResearchForm onSubmit={handleNewResearch} />
        )}
        
        {activeTab === 'results' && (
          <ResearchResults 
            job={currentJob} 
            onJobUpdate={setCurrentJob}
          />
        )}
        
        {activeTab === 'jobs' && (
          <JobsList 
            jobs={jobs} 
            onSelectJob={handleSelectJob}
            onRefresh={loadJobs}
          />
        )}
      </main>
    </div>
  );
}

export default App;