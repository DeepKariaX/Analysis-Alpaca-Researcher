import React from 'react';
import { researchAPI } from '../services/api';

const JobsList = ({ jobs, onSelectJob, onRefresh }) => {
  const handleDeleteJob = async (jobId, event) => {
    event.stopPropagation(); // Prevent triggering onSelectJob
    
    if (window.confirm('Are you sure you want to delete this research job?')) {
      try {
        await researchAPI.deleteJob(jobId);
        onRefresh(); // Refresh the jobs list
      } catch (error) {
        console.error('Failed to delete job:', error);
        alert('Failed to delete job. Please try again.');
      }
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'queued': return '#ffeaa7';
      case 'researching': return '#74b9ff';
      case 'generating': return '#a29bfe';
      case 'completed': return '#00b894';
      case 'failed': return '#d63031';
      default: return '#ddd';
    }
  };

  const formatDuration = (createdAt, completedAt) => {
    if (!completedAt) return 'In progress...';
    
    const start = new Date(createdAt);
    const end = new Date(completedAt);
    const duration = Math.round((end - start) / 1000);
    
    if (duration < 60) return `${duration}s`;
    if (duration < 3600) return `${Math.round(duration / 60)}m`;
    return `${Math.round(duration / 3600)}h`;
  };

  const sortedJobs = [...jobs].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2>📚 Research History</h2>
          <button onClick={onRefresh} className="btn btn-secondary">
            🔄 Refresh
          </button>
        </div>

        {jobs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
            <h3>No Research Jobs Found</h3>
            <p>Start your first research to see it appear here.</p>
          </div>
        ) : (
          <>
            <div style={{ marginBottom: '1rem', color: '#666', fontSize: '0.9rem' }}>
              Showing {jobs.length} research job{jobs.length !== 1 ? 's' : ''}
            </div>
            
            <div className="jobs-grid">
              {sortedJobs.map((job) => (
                <div
                  key={job.id}
                  className="job-card"
                  onClick={() => onSelectJob(job)}
                >
                  <div className="job-meta">
                    <span 
                      className="status-badge"
                      style={{ 
                        backgroundColor: getStatusColor(job.status),
                        color: job.status === 'queued' ? '#d63031' : 'white'
                      }}
                    >
                      {job.status}
                    </span>
                    <button
                      onClick={(e) => handleDeleteJob(job.id, e)}
                      className="btn btn-danger"
                      style={{ 
                        padding: '0.25rem 0.5rem', 
                        fontSize: '0.8rem',
                        borderRadius: '4px'
                      }}
                    >
                      🗑️
                    </button>
                  </div>

                  <div className="job-query">
                    {job.query.length > 100 
                      ? `${job.query.substring(0, 100)}...` 
                      : job.query
                    }
                  </div>

                  <div className="job-details">
                    <div>
                      <strong>Sources:</strong> {job.sources} • 
                      <strong> Results:</strong> {job.num_results}
                    </div>
                    <div style={{ marginTop: '0.5rem' }}>
                      <strong>Duration:</strong> {formatDuration(job.created_at, job.completed_at)}
                    </div>
                    <div style={{ marginTop: '0.5rem' }}>
                      <strong>Created:</strong> {new Date(job.created_at).toLocaleDateString()} {new Date(job.created_at).toLocaleTimeString()}
                    </div>
                  </div>

                  {job.status !== 'completed' && job.status !== 'failed' && (
                    <div style={{ marginTop: '1rem' }}>
                      <div className="progress-bar" style={{ height: '4px' }}>
                        <div 
                          className="progress-fill"
                          style={{ width: `${job.progress}%` }}
                        ></div>
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.25rem' }}>
                        {job.progress}% complete
                      </div>
                    </div>
                  )}

                  {job.error && (
                    <div style={{
                      background: '#f8d7da',
                      border: '1px solid #f5c6cb',
                      color: '#721c24',
                      padding: '0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                      marginTop: '0.5rem'
                    }}>
                      Error: {job.error.length > 50 ? `${job.error.substring(0, 50)}...` : job.error}
                    </div>
                  )}

                  {job.status === 'completed' && (
                    <div style={{
                      background: '#d4edda',
                      border: '1px solid #c3e6cb',
                      color: '#155724',
                      padding: '0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                      marginTop: '0.5rem'
                    }}>
                      ✅ Report generated successfully
                    </div>
                  )}
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default JobsList;