import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { researchAPI } from '../services/api';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const ResearchResults = ({ job, onJobUpdate }) => {
  const [progress, setProgress] = useState([]);
  const [isPolling, setIsPolling] = useState(false);
  const reportRef = useRef(null);

  useEffect(() => {
    if (!job) return;

    let pollingTimeout;
    let isComponentMounted = true;

    const pollProgress = async () => {
      try {
        console.log(`Polling progress for job ${job.id}, current status: ${job.status}`);
        const data = await researchAPI.getResearchProgress(job.id);
        
        if (!isComponentMounted) return;
        
        console.log(`Received status update: ${data.job.status}, progress: ${data.job.progress}%`);
        onJobUpdate(data.job);
        setProgress(data.progress || []);

        // Continue polling if job is not in final state
        if (data.job.status !== 'completed' && data.job.status !== 'failed') {
          pollingTimeout = setTimeout(pollProgress, 1000); // Poll every 1 second for faster updates
        } else {
          console.log(`Job ${job.id} reached final status: ${data.job.status}`);
          setIsPolling(false);
        }
      } catch (error) {
        console.error('Failed to fetch progress:', error);
        if (isComponentMounted) {
          setIsPolling(false);
        }
      }
    };

    // Always start with a fresh fetch of the job status
    console.log(`Setting up polling for job ${job.id} with initial status: ${job.status}`);
    setIsPolling(true);
    
    // Start immediately, then continue polling if needed
    pollProgress();

    // Cleanup function
    return () => {
      isComponentMounted = false;
      if (pollingTimeout) {
        clearTimeout(pollingTimeout);
      }
    };
  }, [job?.id, onJobUpdate]);

  const refreshJobStatus = async () => {
    if (!job) return;
    
    try {
      console.log('Manual refresh triggered for job:', job.id);
      const data = await researchAPI.getResearchProgress(job.id);
      onJobUpdate(data.job);
      setProgress(data.progress || []);
      console.log('Manual refresh completed:', data.job.status, data.job.progress + '%');
    } catch (error) {
      console.error('Failed to refresh job status:', error);
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

  const sanitizeFileName = (text) => {
    return text
      .replace(/[^a-zA-Z0-9\s-_]/g, '') // Remove special characters
      .replace(/\s+/g, '_') // Replace spaces with underscores
      .substring(0, 50) // Limit length
      .toLowerCase();
  };

  const downloadReportAsPDF = async () => {
    if (!job?.report || !reportRef.current) return;

    try {
      // Create a sanitized filename from the query and sources
      const title = sanitizeFileName(job.query);
      const sources = job.sources === 'both' ? 'web_academic' : job.sources;
      const filename = `${title}_${sources}.pdf`;

      // Generate PDF from the rendered HTML
      const canvas = await html2canvas(reportRef.current, {
        scale: 2,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff'
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      
      const imgWidth = 210; // A4 width in mm
      const pageHeight = 295; // A4 height in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;

      let position = 0;

      // Add first page
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;

      // Add additional pages if needed
      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }

      // Save the PDF
      pdf.save(filename);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF. Please try again.');
    }
  };

  if (!job) {
    return (
      <div className="card">
        <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
          <h3>No Research Selected</h3>
          <p>Start a new research or select one from the history to view results.</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
          <div>
            <h2>📊 Research Results</h2>
            <p style={{ color: '#666', margin: '0.5rem 0' }}>{job.query}</p>
          </div>
          <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <button 
                onClick={refreshJobStatus}
                style={{
                  background: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '0.25rem 0.5rem',
                  fontSize: '0.8rem',
                  cursor: 'pointer'
                }}
                title="Refresh job status"
              >
                🔄 Refresh
              </button>
              <span 
                className="status-badge"
                style={{ 
                  backgroundColor: getStatusColor(job.status),
                  color: job.status === 'queued' ? '#d63031' : 'white'
                }}
              >
                {job.status}
              </span>
            </div>
            {job.completed_at && (
              <div style={{ fontSize: '0.8rem', color: '#666' }}>
                Completed: {new Date(job.completed_at).toLocaleString()}
              </div>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        {job.status !== 'completed' && job.status !== 'failed' && (
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${job.progress}%` }}
              ></div>
            </div>
            <div className="progress-text">
              {job.progress}% Complete
              {isPolling && <span className="pulse"> • Updating...</span>}
            </div>
          </div>
        )}

        {/* Job Details */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
          gap: '1rem',
          background: '#f8f9fa',
          padding: '1rem',
          borderRadius: '8px',
          marginBottom: '1.5rem'
        }}>
          <div>
            <strong>Sources:</strong> {job.sources}
          </div>
          <div>
            <strong>Results:</strong> {job.num_results}
          </div>
          <div>
            <strong>Job ID:</strong> {job.id}
          </div>
          <div>
            <strong>Created:</strong> {new Date(job.created_at).toLocaleString()}
          </div>
        </div>

        {/* Progress Log */}
        {progress.length > 0 && (
          <div style={{ marginBottom: '2rem' }}>
            <h3>Progress Log</h3>
            <div style={{ maxHeight: '200px', overflowY: 'auto', background: '#f8f9fa', padding: '1rem', borderRadius: '8px' }}>
              {progress.map((item, index) => (
                <div key={index} style={{ 
                  marginBottom: '0.5rem', 
                  paddingBottom: '0.5rem',
                  borderBottom: index < progress.length - 1 ? '1px solid #dee2e6' : 'none'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: '500' }}>{item.message}</span>
                    <span style={{ fontSize: '0.8rem', color: '#666' }}>
                      {new Date(item.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#666' }}>
                    Status: {item.status} • Progress: {item.progress}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error Display */}
        {job.error && (
          <div style={{
            background: '#f8d7da',
            border: '1px solid #f5c6cb',
            color: '#721c24',
            padding: '1rem',
            borderRadius: '8px',
            marginBottom: '1.5rem'
          }}>
            <strong>Error:</strong> {job.error}
          </div>
        )}

        {/* Action Buttons */}
        {job.status === 'completed' && job.report && (
          <div style={{ marginBottom: '2rem' }}>
            <button onClick={downloadReportAsPDF} className="btn btn-secondary">
              📄 Download Report (PDF)
            </button>
          </div>
        )}
      </div>

      {/* Raw Data Section */}
      {job.raw_data && (
        <div className="card">
          <h3>📄 Raw Research Data</h3>
          <div style={{
            background: '#f8f9fa',
            padding: '1rem',
            borderRadius: '8px',
            maxHeight: '400px',
            overflowY: 'auto',
            fontSize: '0.9rem',
            lineHeight: '1.5',
            whiteSpace: 'pre-wrap'
          }}>
            {job.raw_data}
          </div>
        </div>
      )}

      {/* Generated Report */}
      {job.report && (
        <div className="research-report" ref={reportRef}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3>📋 Generated Report</h3>
            <span style={{ fontSize: '0.8rem', color: '#666' }}>
              Formatted with AI • Ready for use
            </span>
          </div>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {job.report}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
};

export default ResearchResults;