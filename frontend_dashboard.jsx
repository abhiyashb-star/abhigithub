/**
 * 🚀 GEMINI PRO AUTOMATION PLATFORM - FRONTEND DASHBOARD
 * React Dashboard with Real-time Automation Control
 */

import React, { useState, useEffect } from 'react';
import { AlertCircle, Zap, Mail, Globe, FileText, BarChart3, Mic, Play, Loader } from 'lucide-react';

const AutomationDashboard = () => {
  const [activeTab, setActiveTab] = useState('email');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [formData, setFormData] = useState({});
  const [reasoningLevel, setReasoningLevel] = useState('medium');

  // API endpoint
  const API_BASE = 'http://localhost:8000';

  // Automation types
  const automations = [
    {
      id: 'email',
      name: 'Email Agent',
      icon: Mail,
      color: 'from-blue-500 to-cyan-500',
      description: 'Automate email processing, classification, and responses',
      endpoint: '/email-agent',
      fields: ['emails', 'action', 'keywords']
    },
    {
      id: 'web_scrape',
      name: 'Web Scraper',
      icon: Globe,
      color: 'from-green-500 to-emerald-500',
      description: 'Extract data from websites intelligently',
      endpoint: '/web-scraper',
      fields: ['url', 'data_type', 'format']
    },
    {
      id: 'document',
      name: 'Document Analyzer',
      icon: FileText,
      color: 'from-purple-500 to-pink-500',
      description: 'Analyze PDFs, text files, and documents',
      endpoint: '/document-analyzer',
      fields: ['file_path', 'query', 'extract_type']
    },
    {
      id: 'data',
      name: 'Data Analyst',
      icon: BarChart3,
      color: 'from-orange-500 to-red-500',
      description: 'Analyze datasets and generate insights',
      endpoint: '/data-analyst',
      fields: ['csv_path', 'analysis_type', 'chart_type']
    },
    {
      id: 'voice',
      name: 'Voice Agent',
      icon: Mic,
      color: 'from-indigo-500 to-blue-500',
      description: 'Real-time voice processing with Gemini Live API',
      endpoint: '/voice-webhook',
      fields: ['transcript', 'language', 'tone']
    }
  ];

  const currentAutomation = automations.find(a => a.id === activeTab);
  const IconComponent = currentAutomation?.icon || Zap;

  // Handle form input
  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Execute automation
  const handleExecute = async () => {
    setIsProcessing(true);
    try {
      const response = await fetch(`${API_BASE}${currentAutomation.endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task_type: activeTab,
          input_data: formData,
          reasoning_level: reasoningLevel,
          use_tools: ['google_search', 'url_context', 'code_execution', 'file_search']
        })
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: error.message });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto">
        <div className="mb-12">
          <h1 className="text-5xl font-bold text-white mb-2">🚀 Gemini Pro Automation</h1>
          <p className="text-slate-400 text-lg">Intelligent automation with Google Gemini 3.1 Pro</p>
        </div>

        {/* Automation Types Grid */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-12">
          {automations.map(auto => (
            <button
              key={auto.id}
              onClick={() => {
                setActiveTab(auto.id);
                setResult(null);
                setFormData({});
              }}
              className={`p-4 rounded-lg transition-all ${
                activeTab === auto.id
                  ? `bg-gradient-to-br ${auto.color} text-white shadow-lg scale-105`
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              <auto.icon className="w-6 h-6 mx-auto mb-2" />
              <p className="text-sm font-semibold">{auto.name}</p>
            </button>
          ))}
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Input Panel */}
          <div className="lg:col-span-2">
            <div className="bg-slate-800 rounded-xl p-8 border border-slate-700">
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
                  <IconComponent className="w-6 h-6" />
                  {currentAutomation?.name}
                </h2>
                <p className="text-slate-400">{currentAutomation?.description}</p>
              </div>

              {/* Input Fields */}
              <div className="space-y-4 mb-6">
                {currentAutomation?.fields.map(field => (
                  <div key={field}>
                    <label className="block text-sm font-semibold text-slate-300 mb-2 capitalize">
                      {field.replace(/_/g, ' ')}
                    </label>
                    {field.includes('type') ? (
                      <select
                        value={formData[field] || ''}
                        onChange={e => handleInputChange(field, e.target.value)}
                        className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                      >
                        <option value="">Select {field}...</option>
                        {field === 'analysis_type' && (
                          <>
                            <option value="summary">Summary Analysis</option>
                            <option value="trends">Trend Analysis</option>
                            <option value="anomalies">Anomaly Detection</option>
                            <option value="correlation">Correlation Analysis</option>
                          </>
                        )}
                        {field === 'data_type' && (
                          <>
                            <option value="prices">Prices</option>
                            <option value="news">News Articles</option>
                            <option value="products">Products</option>
                            <option value="contacts">Contacts</option>
                          </>
                        )}
                      </select>
                    ) : (
                      <input
                        type="text"
                        placeholder={`Enter ${field}...`}
                        value={formData[field] || ''}
                        onChange={e => handleInputChange(field, e.target.value)}
                        className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                      />
                    )}
                  </div>
                ))}
              </div>

              {/* Reasoning Level */}
              <div className="mb-6">
                <label className="block text-sm font-semibold text-slate-300 mb-3">
                  Reasoning Level (affects execution depth)
                </label>
                <div className="flex gap-3">
                  {['low', 'medium', 'high'].map(level => (
                    <button
                      key={level}
                      onClick={() => setReasoningLevel(level)}
                      className={`flex-1 py-2 px-4 rounded-lg font-semibold transition-all ${
                        reasoningLevel === level
                          ? 'bg-blue-500 text-white'
                          : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                      }`}
                    >
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Execute Button */}
              <button
                onClick={handleExecute}
                disabled={isProcessing || Object.keys(formData).length === 0}
                className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 disabled:from-slate-600 disabled:to-slate-700 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all"
              >
                {isProcessing ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    Processing with Gemini...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    Execute Automation
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-1">
            <div className="bg-slate-800 rounded-xl p-8 border border-slate-700 sticky top-8">
              <h3 className="text-xl font-bold text-white mb-4">Results</h3>

              {result ? (
                <div className="space-y-4">
                  {result.error ? (
                    <div className="bg-red-900/20 border border-red-500/50 rounded-lg p-4">
                      <p className="text-red-300 font-semibold flex items-center gap-2">
                        <AlertCircle className="w-4 h-4" />
                        Error
                      </p>
                      <p className="text-red-200 text-sm mt-2">{result.error}</p>
                    </div>
                  ) : (
                    <>
                      <div className="bg-green-900/20 border border-green-500/50 rounded-lg p-4">
                        <p className="text-green-300 font-semibold">✅ Completed</p>
                        <p className="text-green-200 text-sm mt-1">
                          Execution time: {result.execution_time?.toFixed(2)}s
                        </p>
                      </div>

                      {result.result && (
                        <div className="bg-slate-700 rounded-lg p-4">
                          <p className="text-slate-300 text-sm font-mono overflow-auto max-h-96">
                            {JSON.stringify(result.result, null, 2)}
                          </p>
                        </div>
                      )}
                    </>
                  )}
                </div>
              ) : (
                <div className="text-slate-400 text-center py-8">
                  <Zap className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Results will appear here</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Tools Info */}
        <div className="mt-12 bg-slate-800 rounded-xl p-8 border border-slate-700">
          <h3 className="text-xl font-bold text-white mb-4">Available Tools</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {[
              { name: 'Google Search', icon: '🔍' },
              { name: 'URL Context', icon: '🌐' },
              { name: 'Code Execution', icon: '⚙️' },
              { name: 'File Search', icon: '📄' },
              { name: 'Email Sending', icon: '📧' }
            ].map(tool => (
              <div key={tool.name} className="bg-slate-700 rounded-lg p-4 text-center">
                <div className="text-2xl mb-2">{tool.icon}</div>
                <p className="text-sm text-slate-300">{tool.name}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutomationDashboard;
