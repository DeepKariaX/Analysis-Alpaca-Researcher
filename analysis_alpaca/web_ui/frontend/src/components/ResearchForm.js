import React, { useState } from 'react';

const ResearchForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    query: '',
    sources: 'both',
    num_results: 2,
    llm_provider: 'openai',
    model: 'gpt-4'
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    let newFormData = {
      ...formData,
      [name]: type === 'number' ? parseInt(value, 10) : value
    };

    // Auto-update model when provider changes
    if (name === 'llm_provider') {
      if (value === 'openai') {
        newFormData.model = 'gpt-4';
      } else if (value === 'anthropic') {
        newFormData.model = 'claude-3-sonnet-20240229';
      } else if (value === 'groq') {
        newFormData.model = 'llama3-8b-8192';
      }
    }

    setFormData(newFormData);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.query.trim()) {
      alert('Please enter a research query');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Failed to submit research:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const exampleQueries = [
    "Latest developments in quantum computing and their commercial applications",
    "Environmental impact of renewable energy technologies",
    "Artificial intelligence in healthcare: benefits and ethical concerns",
    "Climate change mitigation strategies and their effectiveness",
    "Blockchain technology applications beyond cryptocurrency"
  ];

  return (
    <div className="card">
      <h2>🔍 Start New Research</h2>
      <p style={{ color: '#666', marginBottom: '2rem' }}>
        Enter your research topic and our AI will search through web and academic sources 
        to generate a comprehensive report.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="query">Research Query *</label>
          <textarea
            id="query"
            name="query"
            className="form-control"
            placeholder="Enter your research question or topic..."
            value={formData.query}
            onChange={handleInputChange}
            required
            rows={3}
          />
          <small style={{ color: '#666', fontSize: '0.8rem' }}>
            Be specific for better results. Example: "Impact of AI on healthcare diagnosis accuracy"
          </small>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div className="form-group">
            <label htmlFor="sources">Sources</label>
            <select
              id="sources"
              name="sources"
              className="form-control"
              value={formData.sources}
              onChange={handleInputChange}
            >
              <option value="both">Web + Academic</option>
              <option value="web">Web Only</option>
              <option value="academic">Academic Only</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="num_results">Number of Sources</label>
            <select
              id="num_results"
              name="num_results"
              className="form-control"
              value={formData.num_results}
              onChange={handleInputChange}
            >
              <option value={2}>2 sources</option>
              <option value={3}>3 sources</option>
              <option value={4}>4 sources</option>
              <option value={5}>5 sources</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="llm_provider">AI Provider</label>
            <select
              id="llm_provider"
              name="llm_provider"
              className="form-control"
              value={formData.llm_provider}
              onChange={handleInputChange}
            >
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="groq">Groq</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="model">Model</label>
            <select
              id="model"
              name="model"
              className="form-control"
              value={formData.model}
              onChange={handleInputChange}
            >
              {formData.llm_provider === 'openai' ? (
                <>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-4-turbo-preview">GPT-4 Turbo</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                </>
              ) : formData.llm_provider === 'anthropic' ? (
                <>
                  <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
                  <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                  <option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
                </>
              ) : (
                <>
                  <option value="llama3-8b-8192">Llama 3 8B</option>
                  <option value="llama3-70b-8192">Llama 3 70B</option>
                  <option value="mixtral-8x7b-32768">Mixtral 8x7B</option>
                  <option value="gemma-7b-it">Gemma 7B</option>
                  <option value="gemma2-9b-it">Gemma 2 9B</option>
                </>
              )}
            </select>
          </div>
        </div>

        <div style={{ marginTop: '2rem' }}>
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={isSubmitting || !formData.query.trim()}
          >
            {isSubmitting ? (
              <>
                <div className="loading-spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></div>
                Starting Research...
              </>
            ) : (
              <>
                🚀 Start Research
              </>
            )}
          </button>
        </div>
      </form>

      <div style={{ marginTop: '3rem' }}>
        <h3>💡 Example Research Topics</h3>
        <div style={{ display: 'grid', gap: '0.5rem', marginTop: '1rem' }}>
          {exampleQueries.map((query, index) => (
            <button
              key={index}
              type="button"
              onClick={() => setFormData(prev => ({ ...prev, query }))}
              style={{
                background: 'rgba(79, 172, 254, 0.1)',
                border: '1px solid rgba(79, 172, 254, 0.3)',
                borderRadius: '8px',
                padding: '0.75rem',
                textAlign: 'left',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                fontSize: '0.9rem',
                color: '#333'
              }}
              onMouseOver={(e) => {
                e.target.style.background = 'rgba(79, 172, 254, 0.2)';
              }}
              onMouseOut={(e) => {
                e.target.style.background = 'rgba(79, 172, 254, 0.1)';
              }}
            >
              "{query}"
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ResearchForm;