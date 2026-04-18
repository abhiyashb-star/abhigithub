# 🎤 AGENT 9: VOICE ASSISTANT SPECIFICATION
**Status:** Ready for Implementation  
**Priority:** High  
**Estimated Implementation Time:** 4-6 hours  

---

## 📋 OVERVIEW

**Agent Name:** Voice Assistant Agent  
**Purpose:** Process voice calls, transcribe conversations, analyze sentiment, and generate insights from audio data.  
**Integration:** Gemini 3.1 Pro + Google Cloud Speech-to-Text API  
**Frequency:** Real-time (on-demand) + Scheduled processing

---

## 🎯 CORE FUNCTIONALITY

### 1. **Call Processing Pipeline**
```
Incoming Call/Audio
     ↓
Audio Recording/Upload
     ↓
Speech-to-Text Conversion (Google Cloud)
     ↓
Transcription Cleanup & Formatting
     ↓
Sentiment Analysis (Gemini)
     ↓
Key Insights Extraction
     ↓
Action Items Identification
     ↓
Follow-up Email Generation
     ↓
Database Storage & Dashboard Display
```

### 2. **Features**

#### A. **Voice Recording & Processing**
- Record incoming calls (with consent)
- Accept uploaded audio files (.mp3, .wav, .m4a, .ogg)
- Support multiple languages (Hindi, English, Gujarati, Marathi, etc.)
- Automatic language detection

#### B. **Transcription Service**
- Real-time transcription (live calls)
- Batch processing (uploaded files)
- Speaker diarization (identify who said what)
- Timestamp markers for key moments
- Accuracy: 95%+ (Google Cloud Speech API)

#### C. **Sentiment Analysis**
```
Analysis Levels:
- Overall sentiment (Positive, Negative, Neutral, Mixed)
- Emotional tone (Excited, Frustrated, Calm, Urgent)
- Confidence score (0-100%)
- Emotion timeline (sentiment by topic)
```

#### D. **Insight Extraction**
Automatically identify:
- Customer pain points
- Product feedback
- Buying signals
- Objections & concerns
- Next steps mentioned
- Competitor mentions
- Budget indicators

#### E. **Action Items**
- Extract all action items
- Assign owners (AI + Human)
- Set due dates
- Priority levels
- Integration with calendar

#### F. **Report Generation**
- Auto-generated call summary
- Key quotes extraction
- Performance metrics
- Conversation quality score
- Recommended follow-up actions

---

## 💾 DATABASE SCHEMA

```sql
CREATE TABLE voice_calls (
    id UUID PRIMARY KEY,
    call_id VARCHAR(255),
    call_date TIMESTAMP,
    duration_seconds INT,
    caller_name VARCHAR(255),
    caller_phone VARCHAR(20),
    recording_url TEXT,
    
    -- Transcription
    transcription TEXT,
    language_detected VARCHAR(10),
    transcription_confidence FLOAT,
    
    -- Sentiment Analysis
    overall_sentiment VARCHAR(20), -- positive, negative, neutral, mixed
    emotion_tone VARCHAR(50),
    sentiment_score FLOAT,
    
    -- Key Insights
    pain_points TEXT[], -- Array
    feedback TEXT[],
    buying_signals TEXT[],
    objections TEXT[],
    
    -- Follow-up
    action_items JSONB,
    follow_up_email TEXT,
    next_steps TEXT,
    
    -- Metadata
    agent_id VARCHAR(50),
    processed_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    
    -- Indexing
    INDEX idx_call_date (call_date),
    INDEX idx_sentiment (overall_sentiment),
    INDEX idx_caller_phone (caller_phone)
);

CREATE TABLE call_transcripts (
    id UUID PRIMARY KEY,
    call_id UUID REFERENCES voice_calls(id),
    speaker_name VARCHAR(255),
    speaker_role VARCHAR(50), -- customer, agent, unknown
    start_time FLOAT,
    end_time FLOAT,
    text TEXT,
    emotion VARCHAR(50),
    sentiment VARCHAR(20),
    created_at TIMESTAMP
);

CREATE TABLE call_action_items (
    id UUID PRIMARY KEY,
    call_id UUID REFERENCES voice_calls(id),
    action_item TEXT,
    owner VARCHAR(255),
    due_date DATE,
    priority INT, -- 1=Critical, 2=High, 3=Medium, 4=Low
    status VARCHAR(50), -- pending, in_progress, completed
    created_at TIMESTAMP
);
```

---

## 🔌 API INTEGRATION

### Required APIs:

**1. Google Cloud Speech-to-Text API**
```
Endpoint: https://speech.googleapis.com/v1/speech:recognize
Authentication: Service Account Key (JSON)
Cost: $0.024 per 15 seconds (first 60 minutes free/month)

Setup:
1. Create Google Cloud Project
2. Enable Speech-to-Text API
3. Create Service Account
4. Store credentials in .env as GOOGLE_SPEECH_API_KEY
```

**2. Google Cloud Speech Stream API** (for real-time)
```
Use gRPC for streaming audio processing
Latency: < 100ms
Cost: Same as batch processing
```

**3. Gemini 3.1 Pro API** (for sentiment & insights)
```
Model: gemini-3.1-pro
Input: Transcription text
Output: JSON with sentiment, insights, action items
Cost: Included in existing API usage
```

---

## 🛠️ IMPLEMENTATION STEPS

### Step 1: Backend Setup (2 hours)
```python
# voice_assistant_agent.py

import google.cloud.speech as speech
from google.cloud.speech import SpeechClient
from google.api_core.gapic_v1 import client_info as grpc_client_info
import json
from typing import Dict, List
import asyncio

class VoiceAssistantAgent:
    def __init__(self):
        self.speech_client = SpeechClient()
        self.gemini_client = genai.Client()
        
    async def process_audio_file(self, file_path: str, language_code: str = "en-US"):
        """Process uploaded audio file"""
        with open(file_path, "rb") as audio_file:
            content = audio_file.read()
        
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.AUTO,
            language_code=language_code,
            enable_speaker_diarization=True,
            diarization_speaker_count=2,
            model="latest_long",
        )
        
        operation = self.speech_client.long_running_recognize(config=config, audio=audio)
        response = operation.result(timeout=300)
        
        return self.parse_transcription(response)
    
    def analyze_sentiment_and_insights(self, transcription: str) -> Dict:
        """Use Gemini to analyze sentiment and extract insights"""
        
        prompt = f"""
        Analyze this call transcription and provide:
        1. Overall sentiment (positive/negative/neutral/mixed)
        2. Emotional tone
        3. Customer pain points
        4. Product feedback
        5. Buying signals
        6. Objections
        7. Competitor mentions
        8. Budget indicators
        9. Key quotes
        10. Recommended follow-up
        
        Transcription:
        {transcription}
        
        Return as JSON format.
        """
        
        response = self.gemini_client.generate_content(prompt)
        return json.loads(response.text)
    
    def generate_follow_up_email(self, call_summary: Dict, customer_name: str) -> str:
        """Generate personalized follow-up email"""
        
        prompt = f"""
        Generate a professional follow-up email based on this call:
        
        Customer: {customer_name}
        Summary: {call_summary}
        
        Email should:
        - Thank them for the call
        - Recap key discussion points
        - Address their pain points
        - List next steps with due dates
        - Include call to action
        
        Keep it concise (150-200 words).
        """
        
        response = self.gemini_client.generate_content(prompt)
        return response.text
```

### Step 2: Database Integration (1.5 hours)
```python
# database_schema.py

async def save_call_record(
    call_data: Dict,
    transcription: str,
    sentiment_analysis: Dict,
    action_items: List[Dict]
):
    """Save complete call record to database"""
    
    call_record = {
        "call_id": call_data["call_id"],
        "call_date": call_data["call_date"],
        "duration_seconds": call_data["duration"],
        "caller_name": call_data["caller_name"],
        "caller_phone": call_data["caller_phone"],
        "transcription": transcription,
        "overall_sentiment": sentiment_analysis["sentiment"],
        "emotion_tone": sentiment_analysis["emotion"],
        "sentiment_score": sentiment_analysis["confidence"],
        "pain_points": sentiment_analysis["pain_points"],
        "action_items": action_items,
        "processed_at": datetime.now()
    }
    
    # Insert into PostgreSQL/Supabase
    result = await db.table("voice_calls").insert(call_record).execute()
    
    # Create action item records
    for item in action_items:
        await db.table("call_action_items").insert({
            "call_id": result["id"],
            "action_item": item["action"],
            "owner": item["owner"],
            "due_date": item["due_date"],
            "priority": item["priority"]
        }).execute()
    
    return result["id"]
```

### Step 3: Frontend Dashboard (1.5 hours)
```jsx
// VoiceAssistantDashboard.jsx

import React, { useState, useEffect } from 'react';

export default function VoiceAssistantDashboard() {
  const [calls, setCalls] = useState([]);
  const [selectedCall, setSelectedCall] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleAudioUpload = async (file) => {
    setUploading(true);
    const formData = new FormData();
    formData.append('audio', file);
    
    const response = await fetch('/api/voice/process', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    setCalls([result, ...calls]);
    setUploading(false);
  };

  return (
    <div className="voice-assistant-dashboard">
      <h1>🎤 Voice Assistant</h1>
      
      {/* Upload Section */}
      <div className="upload-section">
        <input 
          type="file" 
          accept="audio/*"
          onChange={(e) => handleAudioUpload(e.target.files[0])}
          disabled={uploading}
        />
        {uploading && <p>Processing audio...</p>}
      </div>

      {/* Call List */}
      <div className="calls-list">
        {calls.map(call => (
          <div 
            key={call.id}
            className="call-card"
            onClick={() => setSelectedCall(call)}
          >
            <div className="call-header">
              <h3>{call.caller_name}</h3>
              <span className={`sentiment ${call.overall_sentiment}`}>
                {call.overall_sentiment}
              </span>
            </div>
            <p>Duration: {call.duration_seconds}s</p>
            <p>Sentiment Score: {call.sentiment_score}%</p>
          </div>
        ))}
      </div>

      {/* Call Details */}
      {selectedCall && (
        <div className="call-details">
          <h2>Call Details</h2>
          <div className="transcription">
            <h3>Transcription</h3>
            <p>{selectedCall.transcription}</p>
          </div>
          
          <div className="sentiment-analysis">
            <h3>Sentiment Analysis</h3>
            <p>Overall: {selectedCall.overall_sentiment}</p>
            <p>Emotion: {selectedCall.emotion_tone}</p>
            <p>Score: {selectedCall.sentiment_score}%</p>
          </div>

          <div className="insights">
            <h3>Key Insights</h3>
            <ul>
              <li><strong>Pain Points:</strong> {selectedCall.pain_points.join(', ')}</li>
              <li><strong>Feedback:</strong> {selectedCall.feedback.join(', ')}</li>
              <li><strong>Buying Signals:</strong> {selectedCall.buying_signals.join(', ')}</li>
            </ul>
          </div>

          <div className="action-items">
            <h3>Action Items</h3>
            {selectedCall.action_items.map((item, idx) => (
              <div key={idx} className="action-item">
                <p>{item.action}</p>
                <p>Owner: {item.owner} | Due: {item.due_date}</p>
              </div>
            ))}
          </div>

          <button className="send-email-btn">
            Send Follow-up Email
          </button>
        </div>
      )}
    </div>
  );
}
```

### Step 4: API Endpoints (1 hour)
```python
# voice_routes.py

@app.post("/api/voice/process")
async def process_voice_call(file: UploadFile = File(...)):
    """Process uploaded audio file"""
    
    # Save temporary file
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    
    # Initialize agent
    agent = VoiceAssistantAgent()
    
    # Process audio
    transcription = await agent.process_audio_file(temp_path)
    sentiment = agent.analyze_sentiment_and_insights(transcription)
    
    # Save to database
    call_id = await save_call_record(
        call_data={"call_id": str(uuid.uuid4()), ...},
        transcription=transcription,
        sentiment_analysis=sentiment,
        action_items=sentiment["action_items"]
    )
    
    # Clean up
    os.remove(temp_path)
    
    return {"call_id": call_id, "status": "processed"}

@app.get("/api/voice/calls")
async def get_all_calls():
    """Fetch all voice calls"""
    result = await db.table("voice_calls").select("*").execute()
    return result.data

@app.post("/api/voice/calls/{call_id}/send-email")
async def send_follow_up_email(call_id: str):
    """Send generated follow-up email"""
    
    call = await db.table("voice_calls").select("*").eq("id", call_id).single().execute()
    
    agent = VoiceAssistantAgent()
    email_body = agent.generate_follow_up_email(call.data, call.data["caller_name"])
    
    # Send via Gmail API
    await send_email(
        to=call.data["caller_email"],
        subject=f"Follow-up from {call.data['call_date']}",
        body=email_body
    )
    
    return {"status": "email_sent"}
```

---

## 📊 PRICING FOR VOICE ASSISTANT

**Product Tier:** Voice Assistant  
**Price:** ₹5,999 / month  
**Cost Breakdown:**
- Google Speech-to-Text: $0.024 per 15 seconds (~₹20/hour)
- Gemini API: Included
- Database Storage: ₹500/month
- Processing: ₹1,500/month
- **Profit Margin:** 75%+

---

## 🎯 SUCCESS METRICS

- Call processing time: < 30 seconds
- Transcription accuracy: > 95%
- Sentiment prediction accuracy: > 85%
- Action item extraction: > 90%
- User satisfaction: > 4.5/5 stars

---

## ⏰ ROLLOUT TIMELINE

**Week 1:** Backend + API  
**Week 2:** Database + Testing  
**Week 3:** Frontend + Dashboard  
**Week 4:** Production Deployment + Marketing  

---

## 🚀 IMPLEMENTATION PRIORITY

This agent will:
✅ Increase customer engagement  
✅ Generate $2k-3k additional monthly revenue  
✅ Improve conversation quality tracking  
✅ Enable better lead qualification  
✅ Automate follow-up process  

---

**Status:** Ready for Gemini implementation  
**Next Step:** Gemini to code this agent + integrate with existing system  
**Estimated Revenue Impact:** +₹60k-90k/month

