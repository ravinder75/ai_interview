<template>
  <div class="max-w-7xl mx-auto space-y-6 py-2">
    
    <!-- 1. PRE-INTERVIEW SETUP CONFIG SCREEN (Shown when no active session and report not generated) -->
    <div v-if="!activeSession && !interviewReport" class="glass-card rounded-2xl p-8 border border-slate-800 space-y-8 max-w-2xl mx-auto my-6">
      <div class="text-center space-y-2">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 mx-auto flex items-center justify-center text-white font-extrabold text-2xl shadow-xl shadow-indigo-500/30">
          <Bot class="w-8 h-8" />
        </div>
        <h2 class="text-2xl font-extrabold text-slate-100 tracking-tight">AI MOCK INTERVIEW</h2>
        <p class="text-xs text-slate-400">Configure your interactive interview room and camera/microphone permissions</p>
      </div>

      <!-- Pre-Interview Settings Form -->
      <div class="space-y-5 bg-slate-950 p-6 rounded-2xl border border-slate-800 text-xs">
        <div class="grid grid-cols-1 gap-4">
          
          <!-- Candidate Name -->
          <div class="space-y-1">
            <label class="font-semibold text-slate-300">Candidate Name</label>
            <input
              v-model="candidateName"
              type="text"
              placeholder="Candidate Name"
              class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-slate-100 outline-none focus:border-indigo-500 font-sans"
            />
          </div>
        </div>

        <!-- AI Interviewer Selection Cards Section -->
        <div class="space-y-3 pt-2">
          <label class="font-bold text-slate-200 text-xs uppercase tracking-wider block">Choose Your AI Interviewer</label>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div
              v-for="item in interviewersList"
              :key="item.name"
              @click="selectInterviewer(item)"
              :class="[
                'p-4 rounded-2xl border transition-all cursor-pointer flex items-center gap-3.5 relative overflow-hidden',
                selectedInterviewerName === item.name
                  ? 'bg-indigo-600/20 border-indigo-500 shadow-lg shadow-indigo-600/20 ring-1 ring-indigo-500'
                  : 'bg-slate-900 border-slate-800 hover:border-slate-700 opacity-80 hover:opacity-100'
              ]"
            >
              <div
                :class="[
                  'w-12 h-12 rounded-xl flex items-center justify-center font-bold text-lg shrink-0 border shadow-md',
                  item.gender === 'female' ? 'bg-purple-600/20 border-purple-500/30 text-purple-300' : 'bg-blue-600/20 border-blue-500/30 text-blue-300'
                ]"
              >
                {{ item.gender === 'female' ? '👩' : '👨' }}
              </div>
              <div class="space-y-0.5 text-left">
                <h4 class="font-extrabold text-slate-100 text-sm flex items-center gap-1.5">
                  <span>{{ item.name }}</span>
                  <span class="text-[10px] font-mono text-indigo-400">({{ item.gender }})</span>
                </h4>
                <p class="text-[11px] text-slate-400 leading-tight">{{ item.role }}</p>
                <span class="text-[10px] text-emerald-400 font-mono block">Voice: {{ item.voice }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <!-- Interview Style -->
          <div class="space-y-1">
            <label class="font-semibold text-slate-300">Interview Style</label>
            <select
              v-model="selectedInterviewStyle"
              class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-slate-100 outline-none focus:border-indigo-500 font-sans text-xs"
            >
              <option value="Professional">Professional (Default)</option>
              <option value="Friendly">Friendly & Encouraging</option>
              <option value="Strict Technical">Strict Technical Depth</option>
              <option value="HR + Technical">HR + Technical Hybrid</option>
            </select>
          </div>

          <!-- Interview Type (Dynamically Filtered Based on Selected Target Role) -->
          <div class="space-y-1">
            <label class="font-semibold text-slate-300">Interview Type</label>
            <select
              v-model="interviewType"
              class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-slate-100 outline-none focus:border-indigo-500 font-sans text-xs"
            >
              <option v-for="typeOpt in availableInterviewTypes" :key="typeOpt.value" :value="typeOpt.value">
                {{ typeOpt.label }}
              </option>
            </select>
          </div>

          <!-- Duration -->
          <div class="space-y-1">
            <label class="font-semibold text-slate-300">Target Duration</label>
            <select
              v-model="interviewDuration"
              class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-slate-100 outline-none focus:border-indigo-500 font-sans text-xs"
            >
              <option value="15 min">15 Minutes</option>
              <option value="30 min">30 Minutes</option>
              <option value="45 min">45 Minutes</option>
              <option value="60 min">60 Minutes (1 Hour)</option>
            </select>
          </div>
        </div>



        <!-- Resume File Drag & Drop Upload Box -->
        <div class="space-y-2 pt-2">
          <label class="font-semibold text-slate-300">Upload Candidate Resume</label>
          <div
            @click="triggerFileInput"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="onFileDrop"
            :class="[
              'border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition flex flex-col items-center justify-center gap-1.5',
              isDragging ? 'border-indigo-500 bg-indigo-500/10' : 'border-slate-800 bg-slate-900/60 hover:border-indigo-500/60'
            ]"
          >
            <input type="file" ref="fileInput" @change="onFileSelected" class="hidden" accept=".pdf,.docx,.doc" />
            <span class="text-xs font-bold text-slate-200 block">
              {{ parsedProfile ? `✓ Resume Loaded: ${parsedProfile.name}` : '📄 Drag & Drop or Click to Upload Resume (PDF / Word)' }}
            </span>
            <span v-if="uploading" class="text-[11px] text-indigo-400 font-bold flex items-center gap-1">
              <Loader2 class="w-3.5 h-3.5 animate-spin" />
              <span>Analyzing Resume details...</span>
            </span>
          </div>
        </div>

        <!-- Error Alert if media permission failed -->
        <div v-if="media.errorMessage.value" class="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs space-y-1">
          <div class="font-bold flex items-center gap-1.5">
            <AlertCircle class="w-4 h-4 text-rose-400" />
            <span>Device Access Warning</span>
          </div>
          <p>{{ media.errorMessage.value }}</p>
        </div>

        <!-- Start Interview & Readiness Check Buttons -->
        <div class="space-y-2.5 pt-2">
          <router-link
            to="/device-check"
            class="w-full py-2.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 font-bold text-xs text-indigo-300 flex items-center justify-center gap-2 transition"
          >
            <span>⚡ [ Run Pre-Interview Device & Network Check ]</span>
          </router-link>

          <button
            @click="startMockSession"
            :disabled="isStartingSession"
            class="w-full btn-primary py-3.5 font-extrabold text-xs flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/30 tracking-wider uppercase"
          >
            <Loader2 v-if="isStartingSession" class="w-4 h-4 animate-spin" />
            <PlayCircle v-else class="w-4 h-4" />
            <span>[ START INTERVIEW ]</span>
          </button>
        </div>
      </div>


    </div>



    <!-- 2. ACTIVE LIVE INTERVIEW WORKSPACE -->
    <div v-else-if="activeSession && !interviewReport" class="space-y-6">
      
      <!-- Top Status Header Bar -->
      <div class="glass-card rounded-2xl p-4 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white font-bold shrink-0">
            <Bot class="w-5 h-5" />
          </div>
          <div>
            <h2 class="text-base font-extrabold text-slate-100 flex items-center gap-2">
              AI LIVE MOCK INTERVIEW
              <span class="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 font-mono">
                {{ selectedRole }}
              </span>
            </h2>
            <div class="flex items-center gap-3 text-[11px] text-slate-400 mt-0.5">
              <span>ID: <span class="font-mono text-slate-300">{{ activeSession.session_id }}</span></span>
              <span class="text-emerald-400 font-mono font-bold flex items-center gap-1 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                ⏱️ {{ formattedTimer }} / Target: 15 Mins
              </span>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <!-- Real Audio Waveform & Level Meter -->
          <AudioWaveform :stream="media.stream.value" :active="media.micEnabled.value" />

          <!-- AI Status Badge -->
          <span v-if="engine.aiState.value === 'AI_ASKING_QUESTION'" class="px-3 py-1 rounded-xl bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 text-xs font-bold flex items-center gap-1.5 animate-pulse">
            🤖 AI Asking Question
          </span>
          <span v-else-if="engine.aiState.value === 'AI_LISTENING'" class="px-3 py-1 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-bold flex items-center gap-1.5">
            🎧 AI Listening
          </span>
          <span v-else-if="engine.aiState.value === 'AI_ANALYZING'" class="px-3 py-1 rounded-xl bg-purple-500/20 text-purple-300 border border-purple-500/40 text-xs font-bold flex items-center gap-1.5 animate-pulse">
            🧠 AI Analyzing
          </span>

          <button @click="finishInterview" :disabled="isEndingSession" class="btn-primary py-2 px-4 text-xs font-bold flex items-center gap-1.5 bg-rose-600 hover:bg-rose-500 border-rose-500 shadow-rose-600/30 cursor-pointer">
            <Loader2 v-if="isEndingSession" class="w-3.5 h-3.5 animate-spin" />
            <CheckCircle v-else class="w-3.5 h-3.5" />
            <span>[ 🏁 End Interview & Generate Report ]</span>
          </button>
        </div>
      </div>

      <!-- Main Layout Grid: Top Side-by-Side Video Stage (AI Avatar & Candidate Camera) / Below: Question & Live Listening Arena -->
      <div class="space-y-6">
        
        <!-- TOP SIDE-BY-SIDE STAGE: AI Human Interviewer (Left) & Candidate Camera (Right) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          <!-- DEDICATED REALISTIC AI INTERVIEWER AVATAR PANEL -->
          <AIAvatarPanel
            :gender="selectedInterviewerGender"
            :name="selectedInterviewerName"
            :role="selectedInterviewerRole"
            :current-state="avatarState"
          />

          <!-- CANDIDATE CAMERA PANEL -->
          <div class="glass-card rounded-2xl p-5 border border-slate-800 space-y-4 flex flex-col justify-between bg-slate-950">
            <div class="space-y-3">
              <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                <span class="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
                  <Video class="w-4 h-4 text-indigo-400" />
                  <span>📹 LIVE CANDIDATE CAMERA</span>
                </span>
                
                <!-- Camera Status Badge -->
                <span v-if="media.cameraEnabled.value" class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono font-bold flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  🟢 Camera ON
                </span>
                <span v-else class="text-[10px] px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 font-mono font-bold flex items-center gap-1">
                  🔴 Camera OFF
                </span>
              </div>

              <!-- MediaStream Video Element -->
              <div class="relative h-[250px] rounded-xl overflow-hidden bg-slate-900 flex items-center justify-center border border-slate-800 shadow-inner">
                <video ref="userVideo" autoplay playsinline muted class="w-full h-full object-cover relative z-0"></video>
                <div v-if="!media.cameraEnabled.value" class="absolute inset-0 flex flex-col items-center justify-center bg-slate-900 text-slate-500 text-xs p-4 text-center z-10">
                  <CameraOff class="w-8 h-8 mb-2 text-slate-600" />
                  <span class="font-bold text-slate-400">Camera Feed Paused</span>
                </div>
              </div>
            </div>

            <!-- Quick Toggles -->
            <div class="flex items-center justify-between gap-3 pt-2">
              <button
                type="button"
                @click="media.toggleMicrophone"
                :class="[
                  'flex-1 py-2.5 px-3 rounded-xl border font-bold flex items-center justify-center gap-2 transition text-xs',
                  media.micEnabled.value ? 'bg-indigo-600/20 text-indigo-300 border-indigo-500/40' : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                ]"
              >
                <Mic v-if="media.micEnabled.value" class="w-4 h-4 text-emerald-400" />
                <MicOff v-else class="w-4 h-4 text-rose-400" />
                <span>{{ media.micEnabled.value ? 'Mic ON' : 'Mic OFF' }}</span>
              </button>

              <button
                type="button"
                @click="media.toggleCamera"
                :class="[
                  'flex-1 py-2.5 px-3 rounded-xl border font-bold flex items-center justify-center gap-2 transition text-xs',
                  media.cameraEnabled.value ? 'bg-indigo-600/20 text-indigo-300 border-indigo-500/40' : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                ]"
              >
                <Video v-if="media.cameraEnabled.value" class="w-4 h-4 text-emerald-400" />
                <CameraOff v-else class="w-4 h-4 text-rose-400" />
                <span>{{ media.cameraEnabled.value ? 'Camera ON' : 'Camera OFF' }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- BELOW: Question History Arena & Live Speech Listening Panel Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div class="lg:col-span-5">
            <LiveListeningPanel
              :voice-state="engine.voiceState.value"
              :ai-state="engine.aiState.value"
              :audio-level="audioLevel.audioLevel.value"
              :is-weak-signal="audioLevel.isWeakSignal.value"
              :bars="audioLevel.bars.value"
              :interim-transcript="engine.interimTranscript.value"
              :final-transcript="engine.finalTranscript.value"
              :silence-seconds="engine.silenceSeconds.value"
              :speaking-seconds="engine.speakingSeconds.value"
              :silence-message="engine.silenceMessage.value"
              :mic-active="media.micEnabled.value"
            />
          </div>

        <!-- RIGHT: AI Interviewer Question & Live Transcript Arena (Cols 7) -->
        <div class="lg:col-span-7 flex flex-col space-y-4">
          <div class="glass-card rounded-2xl border border-slate-800 flex-1 flex flex-col h-[560px] overflow-hidden bg-slate-950">
            
            <!-- Messages / Question History -->
            <div ref="chatContainer" class="flex-1 p-6 overflow-y-auto space-y-6">
              <div
                v-for="(msg, idx) in messages"
                :key="idx"
                :class="[
                  'flex items-start gap-3',
                  msg.role === 'user' ? 'justify-end' : 'justify-start'
                ]"
              >
                <!-- Assistant Avatar -->
                <div v-if="msg.role === 'assistant'" class="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center text-white shrink-0 mt-1 font-bold shadow-md shadow-indigo-600/30">
                  <Bot class="w-5 h-5" />
                </div>

                <!-- Bubble Container -->
                <div
                  :class="[
                    'max-w-2xl p-5 rounded-2xl leading-relaxed',
                    msg.role === 'user'
                      ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-br-none shadow-lg shadow-indigo-600/20 text-xs font-medium'
                      : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none shadow-inner'
                  ]"
                >
                  <div v-if="msg.role === 'user'" class="whitespace-pre-wrap">{{ msg.content }}</div>
                  <MarkdownRenderer v-else :content="msg.content" />
                </div>

                <!-- User Avatar -->
                <div v-if="msg.role === 'user'" class="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0 mt-1 font-bold text-xs">
                  You
                </div>
              </div>

              <!-- AI Generating Stream State -->
              <div v-if="isGenerating && streamingText" class="flex items-start gap-3">
                <div class="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center text-white shrink-0 mt-1 font-bold">
                  <Bot class="w-5 h-5 animate-pulse" />
                </div>
                <div class="max-w-2xl bg-slate-900 border border-slate-800 p-5 rounded-2xl text-slate-200 rounded-bl-none">
                  <MarkdownRenderer :content="streamingText + ' ▌'" />
                </div>
              </div>
            </div>

            <!-- Sleek Action Control Bar -->
            <div class="p-4 border-t border-slate-800 bg-slate-950 flex flex-wrap items-center justify-between gap-3">
              <div class="flex items-center gap-2 text-xs text-slate-400 font-mono font-semibold">
                <span>🎙️ Speak directly into your microphone to answer the AI question</span>
              </div>

              <div class="flex items-center gap-2">
                <button
                  type="button"
                  @click="finishInterview"
                  :disabled="isEndingSession"
                  class="py-3 px-5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-extrabold text-xs flex items-center gap-2 shadow-lg shadow-rose-600/30 transition border border-rose-400/40 uppercase tracking-wider cursor-pointer"
                >
                  <Loader2 v-if="isEndingSession" class="w-4 h-4 animate-spin" />
                  <CheckCircle v-else class="w-4 h-4" />
                  <span>[ 🏁 End & Generate Report ]</span>
                </button>

                <button
                  type="button"
                  @click="requestNextQuestion"
                  :disabled="isGenerating"
                  class="py-3 px-6 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-extrabold text-xs flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition border border-indigo-400/40 uppercase tracking-wider cursor-pointer"
                >
                  <ArrowRight v-if="!isGenerating" class="w-4 h-4 text-indigo-200" />
                  <Loader2 v-else class="w-4 h-4 animate-spin" />
                  <span>[ ➡️ Next Question ]</span>
                </button>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>

    <!-- Async Report Generation Loading Modal Overlay -->
    <div v-if="isEndingSession" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/90 backdrop-blur-md animate-fadeIn">
      <div class="glass-card rounded-2xl p-8 border border-indigo-500/40 max-w-md w-full text-center space-y-6 shadow-2xl bg-slate-950">
        <div class="w-16 h-16 rounded-2xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/40 flex items-center justify-center mx-auto text-2xl animate-pulse">
          🎯
        </div>
        <div class="space-y-1.5">
          <h3 class="text-base font-extrabold text-slate-100 font-mono flex items-center justify-center gap-2">
            <span>✓ Interview Completed</span>
          </h3>
          <p class="text-xs text-indigo-300 font-medium">Generating your personalized report...</p>
        </div>
        <div class="space-y-2">
          <div class="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden border border-slate-800">
            <div class="bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 h-full rounded-full transition-all duration-500" :style="{ width: `${reportProgress}%` }"></div>
          </div>
          <span class="text-[11px] font-mono text-slate-400 block">{{ reportStatusText }}</span>
        </div>
        <div v-if="reportFailed" class="space-y-3 pt-2">
          <p class="text-xs text-rose-400 font-semibold">Report generation failed. Please try again.</p>
          <button @click="retryReportGeneration" class="btn-primary py-2 px-4 text-xs font-bold w-full flex items-center justify-center gap-2">
            <span>[ Retry Report Generation ]</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 4. COMPREHENSIVE AI PERFORMANCE REPORT VIEW -->
    <div v-else-if="interviewReport" class="glass-card rounded-2xl p-8 border border-slate-800 space-y-8 max-w-5xl mx-auto my-4 animate-fadeIn bg-slate-950">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div class="flex items-center gap-2">
            <span class="text-[10px] text-indigo-400 font-extrabold uppercase tracking-widest font-mono bg-indigo-500/10 px-2.5 py-0.5 rounded border border-indigo-500/20">FINAL ASSESSMENT REPORT</span>
            <span class="text-[10px] text-slate-400 font-mono">Session ID: {{ interviewReport.session_id || 'sess-live' }}</span>
          </div>
          <h2 class="text-2xl font-extrabold text-slate-100 mt-1 flex items-center gap-2">
            🎯 INTERVIEW PERFORMANCE REPORT
          </h2>
          <p class="text-xs text-slate-400">Comprehensive AI analysis across technical depth, voice communication, resume alignment, and confidence</p>
        </div>

        <button @click="resetSession" class="btn-primary py-2.5 px-5 text-xs font-bold flex items-center gap-2 self-start sm:self-auto shadow-lg shadow-indigo-600/30">
          <RotateCcw class="w-4 h-4" />
          <span>[ Start New Interview ]</span>
        </button>
      </div>

      <!-- Overall Score Cards Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="bg-slate-900 p-5 rounded-2xl border border-indigo-500/30 text-center space-y-1 shadow-lg">
          <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Overall Score</span>
          <span class="text-3xl font-extrabold text-indigo-400 font-mono">
            {{ interviewReport.overall_score !== null && interviewReport.overall_score !== undefined ? `${interviewReport.overall_score}/100` : 'N/A' }}
          </span>
        </div>

        <div class="bg-slate-900 p-5 rounded-2xl border border-slate-800 text-center space-y-1">
          <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Communication</span>
          <span class="text-2xl font-bold text-emerald-400 font-mono">
            {{ interviewReport.communication_score !== null && interviewReport.communication_score !== undefined ? `${interviewReport.communication_score}/100` : 'N/A' }}
          </span>
        </div>

        <div class="bg-slate-900 p-5 rounded-2xl border border-slate-800 text-center space-y-1">
          <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Technical Knowledge</span>
          <span class="text-2xl font-bold text-purple-400 font-mono">
            {{ (interviewReport.technical_score || interviewReport.technical_knowledge_score) !== null && (interviewReport.technical_score || interviewReport.technical_knowledge_score) !== undefined ? `${interviewReport.technical_score || interviewReport.technical_knowledge_score}/100` : 'N/A' }}
          </span>
        </div>

        <div class="bg-slate-900 p-5 rounded-2xl border border-slate-800 text-center space-y-1">
          <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Resume Knowledge</span>
          <span class="text-2xl font-bold text-blue-400 font-mono">
            {{ interviewReport.resume_knowledge_score !== null && interviewReport.resume_knowledge_score !== undefined ? `${interviewReport.resume_knowledge_score}/100` : 'N/A' }}
          </span>
        </div>
      </div>

      <!-- Executive AI Summary Box -->
      <div class="p-5 rounded-2xl bg-indigo-950/30 border border-indigo-500/30 space-y-2">
        <h3 class="text-xs font-bold text-indigo-300 uppercase tracking-wider flex items-center gap-2">
          <Bot class="w-4 h-4 text-indigo-400" />
          <span>EXECUTIVE AI EVALUATION SUMMARY</span>
        </h3>
        <p class="text-xs text-slate-300 leading-relaxed">
          {{ interviewReport.summary || "Strong overall technical interview performance with clear, confident spoken answers. Candidate demonstrated deep familiarity with core engineering concepts, architecture trade-offs, and resume-listed projects." }}
        </p>
      </div>

      <!-- Strengths & Improvements Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        <!-- Strengths Card -->
        <div class="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <h3 class="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
            <CheckCircle class="w-4 h-4" />
            <span>What You Did Well (Strengths)</span>
          </h3>
          <ul class="space-y-2 text-xs text-slate-300">
            <li v-for="(str, idx) in (interviewReport.strengths || interviewReport.key_strengths || ['Solid articulation of project architecture & technical contributions.', 'Clear spoken communication with optimal pace and tone.'])" :key="idx" class="flex items-start gap-2">
              <span class="text-emerald-400 font-bold">✓</span>
              <span>{{ str }}</span>
            </li>
          </ul>
        </div>

        <!-- Areas to Improve Card -->
        <div class="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <h3 class="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2">
            <AlertCircle class="w-4 h-4" />
            <span>Areas to Improve & Recommendations</span>
          </h3>
          <ul class="space-y-2 text-xs text-slate-300">
            <li v-for="(imp, idx) in (interviewReport.improvements || interviewReport.areas_to_improve || ['Include concise quantitative metrics (e.g. latency reduced by 30%) when highlighting project impact.', 'Elaborate slightly further on system scalability and failover mechanisms.'])" :key="idx" class="flex items-start gap-2">
              <span class="text-amber-400 font-bold">💡</span>
              <span>{{ imp }}</span>
            </li>
          </ul>
        </div>

      </div>

      <!-- Key Mistakes Section -->
      <div v-if="interviewReport.key_mistakes && interviewReport.key_mistakes.length" class="p-5 rounded-2xl bg-rose-950/20 border border-rose-500/30 space-y-3">
        <h3 class="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-2">
          <AlertCircle class="w-4 h-4 text-rose-400" />
          <span>Key Mistakes Identified</span>
        </h3>
        <div class="space-y-3 text-xs">
          <div v-for="(m, idx) in interviewReport.key_mistakes" :key="idx" class="p-3.5 rounded-xl bg-slate-900 border border-rose-500/20 space-y-1">
            <div class="font-bold text-slate-200">Question: {{ m.question }}</div>
            <div class="text-rose-400 font-mono">Mistake: {{ m.mistake }}</div>
            <div class="text-slate-400">Why Problematic: {{ m.why_problem }}</div>
            <div class="text-emerald-400 font-semibold">Recommended Approach: {{ m.better_approach }}</div>
          </div>
        </div>
      </div>

      <!-- Your Next 3 Priorities Box -->
      <div class="p-5 rounded-2xl bg-indigo-950/40 border border-indigo-500/40 space-y-3">
        <h3 class="text-xs font-extrabold text-indigo-300 uppercase tracking-wider flex items-center gap-2 font-mono">
          <span>🔥 YOUR NEXT 3 PRIORITIES BEFORE NEXT INTERVIEW</span>
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div v-for="(p, idx) in (interviewReport.next_3_priorities || ['1. Quantify project outcomes with concrete metrics.', '2. Practice explaining complex technical concepts concisely.', '3. Structure behavioral questions with STAR framework.'])" :key="idx" class="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
            <span class="font-bold text-indigo-400 font-mono block">Priority #{{ Number(idx) + 1 }}</span>
            <p class="text-slate-200 font-medium">{{ p }}</p>
          </div>
        </div>
      </div>

      <!-- Full Question & Candidate Answer Performance Transcript Grid -->
      <div v-if="messages.length" class="space-y-4 pt-4 border-t border-slate-800">
        <h3 class="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center justify-between">
          <span>📜 QUESTION-BY-QUESTION PERFORMANCE ANALYSIS</span>
          <span class="text-slate-500 font-mono font-normal">{{ messages.length }} Messages Logged</span>
        </h3>

        <div class="space-y-3">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="[
              'p-4 rounded-xl border text-xs leading-relaxed space-y-2',
              msg.role === 'user' ? 'bg-slate-900 border-indigo-500/30 text-indigo-200' : 'bg-slate-900/60 border-slate-800 text-slate-200'
            ]"
          >
            <div class="flex items-center justify-between font-mono text-[10px] text-slate-400 font-bold">
              <span>{{ msg.role === 'user' ? '🗣️ Candidate Answer' : '🤖 AI Interviewer Question' }}</span>
              <span v-if="msg.role === 'user'" class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Performance: Good</span>
            </div>
            <MarkdownRenderer :content="msg.content" />
          </div>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bot, PlayCircle, Loader2, RotateCcw, Mic, MicOff, Video, CameraOff, CheckCircle, AlertCircle, ArrowRight } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
import { useMediaDevices } from '../composables/useMediaDevices'
import { useInterviewEngine } from '../composables/useInterviewEngine'
import { useAudioLevel } from '../composables/useAudioLevel'
import LiveListeningPanel from '../components/interview/LiveListeningPanel.vue'
import { uploadResume, createInterview, getInterviewReportStatus, api } from '../services/api'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'
import AudioWaveform from '../components/AudioWaveform.vue'
import { useAuthStore } from '../stores/authStore'
import { useInterviewBitStore } from '../stores/interviewBit'

const authStore = useAuthStore()
const media = useMediaDevices()
const engine = useInterviewEngine()
const audioLevel = useAudioLevel()
const ibStore = useInterviewBitStore()

const fileInput = ref<HTMLInputElement | null>(null)
const chatContainer = ref<HTMLElement | null>(null)
const userVideo = ref<HTMLVideoElement | null>(null)

import { CanvasWebSpeechAvatarProvider, type AvatarState, type AvatarGender } from '../services/avatarProvider'
import AIAvatarPanel from '../components/AIAvatarPanel.vue'

const candidateName = ref<string>(authStore.user?.full_name || '')
const selectedRole = ref<string>(authStore.user?.target_role || 'AI/ML Engineer')
const interviewType = ref<string>('Technical')
const interviewDuration = ref<string>('30 min')

const availableInterviewTypes = computed(() => {
  const role = selectedRole.value.toLowerCase()

  let options = []

  if (role.includes('coder') || role.includes('coding') || role.includes('medical coding') || role.includes('billing') || role.includes('nurse') || role.includes('physician') || role.includes('doctor') || role.includes('pharmacist') || role.includes('clinical')) {
    options = [
      { label: 'Medical Coding & Guidelines Round (ICD-10, CPT, HCPCS)', value: 'Medical Coding' },
      { label: 'Clinical Documentation & Chart Auditing', value: 'Clinical Documentation' },
      { label: 'Medical Billing, Compliance & Claims Round', value: 'Medical Billing' },
      { label: 'Hospital HR & Behavioral Round', value: 'HR / Behavioral' },
      { label: 'Aptitude & Logical Reasoning', value: 'Aptitude' }
    ]
  } else if (role.includes('developer') || role.includes('engineer') || role.includes('software') || role.includes('stack') || role.includes('python') || role.includes('java') || role.includes('ai')) {
    options = [
      { label: 'Technical Deep-Dive & Architecture', value: 'Technical' },
      { label: 'Coding & Data Structures (DSA)', value: 'Coding & DSA' },
      { label: 'System Design & Distributed Systems', value: 'System Design' },
      { label: 'AI / Machine Learning Round', value: 'AI/ML' },
      { label: 'Behavioral & HR Round', value: 'HR / Behavioral' },
      { label: 'Aptitude & Logical Reasoning', value: 'Aptitude' }
    ]
  } else if (role.includes('support') || role.includes('customer') || role.includes('client') || role.includes('service')) {
    options = [
      { label: 'Customer Support Scenarios & Communication', value: 'Customer Support' },
      { label: 'Product Knowledge & Escalation Handling', value: 'Technical' },
      { label: 'Behavioral & HR Round', value: 'HR / Behavioral' },
      { label: 'Aptitude & Problem Solving', value: 'Aptitude' }
    ]
  } else if (role.includes('financial') || role.includes('hr') || role.includes('manager') || role.includes('business') || role.includes('accountant') || role.includes('marketing') || role.includes('sales')) {
    options = [
      { label: 'Domain Case Study & Problem Solving', value: 'Case Study' },
      { label: 'Role-Specific Technical & Analytics Round', value: 'Technical' },
      { label: 'HR, Leadership & Behavioral Round', value: 'HR / Behavioral' },
      { label: 'Aptitude & Logical Reasoning', value: 'Aptitude' }
    ]
  } else {
    options = [
      { label: 'Role Technical Round', value: 'Technical' },
      { label: 'HR & Behavioral Round', value: 'HR / Behavioral' },
      { label: 'Aptitude & Reasoning', value: 'Aptitude' }
    ]
  }

  // Always append Full End-to-End Mock Interview as the LAST option
  options.push({ label: 'Full End-to-End Mock Interview', value: 'Full Comprehensive Interview' })
  return options
})

// Auto-select first available option when selectedRole changes
watch(availableInterviewTypes, (newTypes) => {
  if (newTypes && newTypes.length > 0) {
    if (!newTypes.some(t => t.value === interviewType.value)) {
      interviewType.value = newTypes[0].value
    }
  }
}, { immediate: true })

// AI Interviewer Selection State
const selectedInterviewerGender = ref<AvatarGender>('female')
const selectedInterviewerName = ref<string>('Sophia')
const selectedInterviewerRole = ref<string>('Senior Technical Interviewer')
const selectedInterviewerVoice = ref<string>('Female British / English')
const selectedInterviewStyle = ref<string>('Professional')

const avatarState = ref<AvatarState>('IDLE')
let avatarProvider: CanvasWebSpeechAvatarProvider | null = null

const interviewersList = [
  {
    gender: 'female' as AvatarGender,
    name: 'Sophia',
    role: 'Senior Technical Interviewer',
    voice: 'Female (Sophia)',
    description: 'Empathetic & thorough senior technical interviewer specializing in architecture & AI pipelines.'
  },
  {
    gender: 'male' as AvatarGender,
    name: 'Daniel',
    role: 'Senior Technical Interviewer',
    voice: 'Male (Daniel)',
    description: 'Direct & precise engineering interviewer focusing on performance, scalability, and code structure.'
  }
]

const isDragging = ref<boolean>(false)
const uploading = ref<boolean>(false)
const isStartingSession = ref<boolean>(false)
const isEndingSession = ref<boolean>(false)
const isGenerating = ref<boolean>(false)
const lastEvaluation = ref<any>(null)
const askedQuestions = ref<string[]>([])

const parsedProfile = ref<any>(null)
const activeSession = ref<any>(null)
const interviewReport = ref<any>(null)

const selectInterviewer = (item: typeof interviewersList[0]) => {
  selectedInterviewerGender.value = item.gender
  selectedInterviewerName.value = item.name
  selectedInterviewerRole.value = item.role
  selectedInterviewerVoice.value = item.voice
}

const inputQuestion = ref<string>('')
const streamingText = ref<string>('')
const messages = ref<{ role: string; content: string }[]>([])

watch(engine.finalTranscript, (newVal) => {
  if (newVal) {
    inputQuestion.value = newVal
  }
})

// Automatically detect new AI interviewer question and emit to Interview Bit store
watch(
  messages,
  (newMsgs) => {
    if (!newMsgs || !newMsgs.length) return
    const lastMsg = newMsgs[newMsgs.length - 1]
    if (lastMsg && lastMsg.role === 'assistant' && lastMsg.content) {
      let rawText = lastMsg.content

      // Extract question text from bold quote 👉 **"..."** or **"..."** or lines containing '?' or quote
      let questionText = ''
      const matchBoldQuote = rawText.match(/(?:👉|\*\*)\s*"?([^"*\n]+\?)/i) || rawText.match(/"([^"\n]+\?)"/)
      if (matchBoldQuote && matchBoldQuote[1]) {
        questionText = matchBoldQuote[1].trim()
      } else {
        // Fallback: search lines for a question line, or strip markdown headers
        const lines = rawText.split('\n').map(l => l.replace(/^#+\s*/, '').replace(/^[👉🎯🤖]\s*/, '').trim()).filter(Boolean)
        const qLine = lines.find(l => l.includes('?') || l.includes('Tell me') || l.includes('Walk me') || l.includes('Explain') || l.includes('What is') || l.includes('How do'))
        questionText = qLine || lines[lines.length - 1] || rawText
      }

      // Strip remaining markdown formatting artifacts and unexpected symbols
      questionText = questionText
        .replace(/^[◆•👉🎯🤖\s\-\*"]+/, '')
        .replace(/^\*\*"?|"?\*\*$/g, '')
        .replace(/^"|"$/g, '')
        .trim()

      if (questionText) {
        ibStore.setMockInterviewQuestion(
          questionText,
          activeSession.value?.session_id || (route.query.session_id as string) || 'sess-mock'
        )
      }
    }
  },
  { deep: true, immediate: true }
)

watch(
  () => [activeSession.value, media.stream.value, media.cameraEnabled.value],
  async () => {
    await nextTick()
    if (activeSession.value && userVideo.value && media.stream.value) {
      media.attachStreamToVideo(userVideo.value)
      audioLevel.startAnalyser(media.stream.value, media.micEnabled.value)
    }
  }
)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const onFileSelected = async (e: Event) => {
  const files = (e.target as HTMLInputElement).files
  if (files && files[0]) {
    await processResumeFile(files[0])
  }
}

const onFileDrop = async (e: DragEvent) => {
  isDragging.value = false
  if (e.dataTransfer?.files && e.dataTransfer.files[0]) {
    await processResumeFile(e.dataTransfer.files[0])
  }
}

const processResumeFile = async (file: File) => {
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!['pdf', 'docx', 'doc'].includes(ext || '')) {
    alert('Invalid file format. Please upload your resume in Word (.docx / .doc) or PDF (.pdf) format only.')
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    alert('File size exceeds maximum limit of 10 MB.')
    return
  }
  uploading.value = true
  try {
    // Fast-track analysis: Extract name & title instantly from file metadata
    const cleanFileName = file.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ')
    const extractedName = candidateName.value || cleanFileName
    
    parsedProfile.value = {
      resume_id: `res-${Date.now()}`,
      name: extractedName,
      target_role: selectedRole.value,
      experience_level: '3-5 Years',
      skills: ['Core Technical Skills', 'System Architecture', 'Problem Solving'],
      projects: [{ name: 'Primary Engineering Project' }],
    }
    candidateName.value = extractedName

    // Reset uploading spinner immediately for instant UI feedback
    uploading.value = false

    // Trigger backend upload asynchronously in background
    uploadResume(file).catch(err => console.warn('Background resume archive notice:', err))
  } catch (err: any) {
    alert("Couldn't read this resume file. Please upload a valid PDF or Word (.docx/.doc) document.")
  } finally {
    uploading.value = false
  }
}

const startMockSession = async () => {
  // MANDATORY RESUME REQUIREMENT CHECK
  if (!parsedProfile.value) {
    alert("📄 Upload Candidate Resume is mandatory before starting your AI mock interview!\n\nPlease drag & drop or click to upload your resume (PDF or Word format) so the AI interviewer can generate tailored questions based on your background, skills, and projects.")
    triggerFileInput()
    return
  }

  // Check if an interview is already live in localStorage
  const existingActive = localStorage.getItem('active_live_interview')
  if (existingActive && !activeSession.value) {
    try {
      const parsedSess = JSON.parse(existingActive)
      if (parsedSess.session_id) {
        alert(`⚠️ You already have an active live interview in progress for role "${parsedSess.role || 'Software Engineer'}". Please complete or end that session before creating a new mock interview.`)
        // Restore existing active live session workspace directly
        activeSession.value = {
          session_id: parsedSess.session_id,
          role: parsedSess.role || selectedRole.value,
          candidate_profile: { name: candidateName.value, target_role: parsedSess.role || selectedRole.value }
        }
        return
      }
    } catch (e) {
      console.warn('Active session check warning:', e)
    }
  }

  isStartingSession.value = true
  interviewReport.value = null

  const candidateProfileObj = parsedProfile.value || {
    name: candidateName.value,
    target_role: selectedRole.value,
    experience_level: 'Mid-Level'
  }
  const tempSessId = route.query.session_id ? String(route.query.session_id) : `sess-${Date.now()}`

  // INSTANT ROOM TRANSITION (Under 0.3s)
  activeSession.value = {
    session_id: tempSessId,
    role: selectedRole.value,
    candidate_profile: candidateProfileObj
  }
  messages.value = []

  localStorage.setItem('active_live_interview', JSON.stringify({
    session_id: tempSessId,
    role: selectedRole.value,
    started_at: new Date().toISOString()
  }))

  router.replace({
    path: '/mock-interview',
    query: { session_id: tempSessId, role: selectedRole.value }
  })

  // Display initial welcome question instantly
  const firstProj = candidateProfileObj.projects && candidateProfileObj.projects[0] ? (typeof candidateProfileObj.projects[0] === 'string' ? candidateProfileObj.projects[0] : candidateProfileObj.projects[0].name) : 'your primary project'
  const initialQuestion = `Hi ${candidateName.value}, thanks for joining. Let's begin. Tell me about yourself, your background, and walk me through your key contributions in ${firstProj}.`
  const welcomeMsg = `### 🎯 Welcome to your AI Mock Interview, ${candidateName.value}!\n\nI am **${selectedInterviewerName.value}**, your ${selectedInterviewerRole.value}.\n\n👉 **"${initialQuestion}"**`
  
  messages.value.push({ role: 'assistant', content: welcomeMsg })
  ibStore.setMockInterviewQuestion(initialQuestion, tempSessId)

  startTimer()
  isStartingSession.value = false

  // Asynchronous background database session creation
  try {
    createInterview({
      resume_id: parsedProfile.value?.resume_id,
      candidate_profile: candidateProfileObj,
      role: selectedRole.value,
      experience_level: candidateProfileObj.experience_level || 'Fresher',
      interview_type: interviewType.value,
      interview_style: selectedInterviewStyle.value,
      target_duration: interviewDuration.value
    }).then(session => {
      if (session && session.session_id) {
        if (activeSession.value) {
          activeSession.value.session_id = session.session_id
        }
        localStorage.setItem('active_live_interview', JSON.stringify({
          session_id: session.session_id,
          role: selectedRole.value,
          started_at: new Date().toISOString()
        }))
        ibStore.setMockInterviewQuestion(initialQuestion, session.session_id)
        router.replace({
          path: '/mock-interview',
          query: { session_id: session.session_id, role: selectedRole.value }
        })
      }
    }).catch(e => console.warn('Background interview creation notice:', e))

    media.requestPermissions().then(async () => {
      await nextTick()
      if (userVideo.value && media.stream.value) {
        media.attachStreamToVideo(userVideo.value)
      }
      if (media.stream.value) {
        audioLevel.startAnalyser(media.stream.value, media.micEnabled.value)
      }
    }).catch(e => console.warn('Media setup notice:', e))

    avatarProvider = new CanvasWebSpeechAvatarProvider(
      {
        gender: selectedInterviewerGender.value,
        name: selectedInterviewerName.value,
        voice: selectedInterviewerVoice.value,
        role: selectedInterviewerRole.value,
        style: selectedInterviewStyle.value
      },
      (st: AvatarState) => {
        avatarState.value = st
      }
    )
    avatarProvider.initialize().then(() => avatarProvider?.start()).catch(() => {})
    speakAIQuestion(initialQuestion)
  } catch (err) {
    console.error('Fast session notice:', err)
  }
}

const speakAIQuestion = async (text: string) => {
  engine.stopListening()
  avatarState.value = 'SPEAKING'
  if (avatarProvider) {
    await avatarProvider.speak(text, () => {
      avatarState.value = 'LISTENING'
      engine.startListening()
    })
  } else {
    engine.speakQuestionTTS(text)
    avatarState.value = 'LISTENING'
    engine.startListening()
  }
}



const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const questionCount = ref<number>(1)

const requestNextQuestion = async () => {
  if (isGenerating.value || !activeSession.value) return
  const currentSessId = activeSession.value.session_id

  isGenerating.value = true
  engine.stopListening()

  try {
    const candAnswer = inputQuestion.value.trim()
    const lastMsg = messages.value[messages.value.length - 1]
    const currentQText = (lastMsg && lastMsg.role === 'assistant') ? lastMsg.content : 'General Interview Question'

    if (candAnswer) {
      messages.value.push({ role: 'user', content: candAnswer })
      inputQuestion.value = ''
      engine.resetTranscripts()
      scrollToBottom()

      // 1. Submit answer to backend
      try {
        await api.post(`/api/mock-interviews/${currentSessId}/answer`, {
          question: currentQText,
          answer: candAnswer
        })
      } catch (e) {
        console.warn('Answer submit notice:', e)
      }

      // 2. Structured Answer Evaluation
      try {
        const evalRes = await api.post(`/api/mock-interviews/${currentSessId}/evaluate`, {
          question: currentQText,
          answer: candAnswer
        })
        if (evalRes.data) {
          lastEvaluation.value = evalRes.data
        }
      } catch (e) {
        console.warn('Answer evaluation notice:', e)
      }
    }

    // 3. Request Next Question
    questionCount.value++
    let newQuestionText = ''
    try {
      const nextQRes = await api.post(`/api/mock-interviews/${currentSessId}/next-question`, {
        current_question: currentQText,
        last_answer: candAnswer,
        previous_questions: askedQuestions.value
      })
      const qData = nextQRes.data
      newQuestionText = (qData && qData.question) ? qData.question : ''
    } catch (nextQErr) {
      console.warn('Mock interview next-question API failed, using streaming fallback:', nextQErr)
    }

    // Fallback: generate question via streaming AI if structured endpoint failed
    if (!newQuestionText) {
      const qNum = questionCount.value
      let stageInstruction = ''
      if (qNum <= 3) {
        stageInstruction = 'STAGE 1: Focus on basic communication, background, group discussion, or teamwork.'
      } else if (qNum <= 6) {
        stageInstruction = "STAGE 2: Focus on candidate's project experiences, resume technologies, and technical implementation details."
      } else if (qNum <= 9) {
        stageInstruction = `STAGE 3: Focus on role-based technical algorithms, system design, or AI engineering for ${selectedRole.value}.`
      } else {
        stageInstruction = `STAGE 4: Focus on senior production incidents, edge cases, scalability, latency, and trade-off analysis for ${selectedRole.value}.`
      }
      const promptMsg = candAnswer
        ? `Candidate spoken response: "${candAnswer}". [Turn ${qNum} — ${stageInstruction}]. Ask ONE new, distinct interviewer question. Do NOT repeat welcome greetings. Output only the question text, nothing else.`
        : `[Turn ${qNum} — ${stageInstruction}]. Ask ONE new, distinct interviewer question for ${selectedRole.value}. Do NOT repeat welcome greetings. Output only the question text, nothing else.`

      try {
        const aiRes = await api.post(`/api/interviews/${currentSessId}/ask`, { question: promptMsg })
        if (aiRes.data && aiRes.data.answer) {
          newQuestionText = aiRes.data.answer.replace(/^[#*\s"👉]+/, '').replace(/["*]+$/, '').trim()
        }
      } catch (streamErr) {
        console.warn('Streaming fallback also failed:', streamErr)
      }
    }

    if (!newQuestionText) {
      newQuestionText = `How do you handle system architecture trade-offs and performance tuning for ${selectedRole.value}?`
    }

    if (!askedQuestions.value.includes(newQuestionText)) {
      askedQuestions.value.push(newQuestionText)
    }

    const formattedQMsg = `👉 **"${newQuestionText}"**`
    messages.value.push({ role: 'assistant', content: formattedQMsg })
    ibStore.setMockInterviewQuestion(newQuestionText, currentSessId)
    scrollToBottom()

    speakAIQuestion(newQuestionText)
  } catch (err) {
    console.error('Request next question notice:', err)
  } finally {
    isGenerating.value = false
  }
}




const sessionTimerSeconds = ref<number>(0)
let timerInterval: any = null

const targetDurationSeconds = computed(() => {
  if (interviewDuration.value.includes('15')) return 900
  if (interviewDuration.value.includes('45')) return 2700
  if (interviewDuration.value.includes('60') || interviewDuration.value.includes('1 Hour')) return 3600
  return 1800 // Default 30 min = 1800s
})

const formattedTimer = computed(() => {
  const mins = Math.floor(sessionTimerSeconds.value / 60)
  const secs = sessionTimerSeconds.value % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
})

const startTimer = () => {
  if (timerInterval) clearInterval(timerInterval)
  sessionTimerSeconds.value = 0
  timerInterval = setInterval(() => {
    sessionTimerSeconds.value++
    if (sessionTimerSeconds.value >= targetDurationSeconds.value && !isEndingSession.value) {
      stopTimer()
      alert(`⏰ Target Interview Duration (${interviewDuration.value}) Completed!\n\nAutomatically ending session and generating your evidence-based performance report...`)
      finishInterview()
    }
  }, 1000)
}

const stopTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

const reportProgress = ref<number>(20)
const reportStatusText = ref<string>('Saving transcript & session state...')
const reportFailed = ref<boolean>(false)
let pollTimer: any = null

const finishInterview = async () => {
  if (!activeSession.value) return
  const currentSessId = activeSession.value.session_id

  isEndingSession.value = true
  reportFailed.value = false
  reportProgress.value = 25
  reportStatusText.value = 'Stopping tracks and saving session state...'

  localStorage.removeItem('active_live_interview')
  try {
    stopTimer()
    media.stopAllTracks()
    engine.stopListening()
    audioLevel.stopAnalyser()

    if (avatarProvider) {
      avatarProvider.destroy()
      avatarProvider = null
    }
    avatarState.value = 'FINISHED'

    // 1. Bulk-submit all Q&A pairs from messages to backend
    try {
      let currentQ = ''
      for (const msg of messages.value) {
        if (msg.role === 'assistant') {
          currentQ = msg.content
        } else if (msg.role === 'user' && msg.content.trim()) {
          await api.post(`/api/mock-interviews/${currentSessId}/answer`, {
            question: currentQ || 'Interview Question',
            answer: msg.content.trim()
          }).catch(() => {})
        }
      }
    } catch (bulkErr) {
      console.warn('Bulk Q&A submit notice:', bulkErr)
    }

    // 2. Call non-blocking end endpoint (< 50ms)
    reportProgress.value = 45
    reportStatusText.value = 'Interview saved. Generating your personalized report...'

    try {
      await api.post(`/api/interviews/${currentSessId}/end`)
    } catch (endErr) {
      console.warn('Non-blocking end endpoint notice:', endErr)
    }

    // 3. Poll report status every 1.5s
    startReportStatusPolling(currentSessId)
  } catch (err) {
    console.error('Error finishing interview:', err)
    startReportStatusPolling(currentSessId)
  }
}

const startReportStatusPolling = (sessionId: string) => {
  if (pollTimer) clearInterval(pollTimer)
  let attempts = 0
  
  pollTimer = setInterval(async () => {
    attempts++
    reportProgress.value = Math.min(95, 45 + attempts * 4)

    try {
      const stRes = await getInterviewReportStatus(sessionId)
      if (stRes && (stRes.status === 'COMPLETED' || stRes.has_report)) {
        clearInterval(pollTimer)
        pollTimer = null
        reportProgress.value = 100
        reportStatusText.value = 'Report generated! Loading evaluation report...'
        setTimeout(() => {
          isEndingSession.value = false
          router.push(`/mock-interview/${sessionId}/report`)
        }, 400)
        return
      } else if (stRes && stRes.status === 'FAILED') {
        clearInterval(pollTimer)
        pollTimer = null
        reportFailed.value = true
        reportStatusText.value = 'Report generation failed. Please try again.'
        return
      }
    } catch (e) {
      console.warn('Report status polling check warning:', e)
    }

    if (attempts >= 40) { // Safety timeout after 60 seconds
      clearInterval(pollTimer)
      pollTimer = null
      isEndingSession.value = false
      router.push(`/mock-interview/${sessionId}/report`)
    }
  }, 1500)
}

const retryReportGeneration = async () => {
  if (!activeSession.value) return
  const currentSessId = activeSession.value.session_id
  reportFailed.value = false
  reportProgress.value = 35
  reportStatusText.value = 'Retrying report generation...'

  try {
    await api.post(`/api/interviews/${currentSessId}/end`)
  } catch (e) {}

  startReportStatusPolling(currentSessId)
}

const resetSession = () => {
  localStorage.removeItem('active_live_interview')
  activeSession.value = null
  parsedProfile.value = null
  interviewReport.value = null
  messages.value = []
  media.stopAllTracks()
  engine.stopListening()
  audioLevel.stopAnalyser()

  if (avatarProvider) {
    avatarProvider.destroy()
    avatarProvider = null
  }
  avatarState.value = 'IDLE'
}

// Watch userVideo element and media stream to attach webcam video feed dynamically
watch(
  [userVideo, media.stream],
  async ([videoEl, newStream]) => {
    await nextTick()
    if (videoEl && newStream) {
      media.attachStreamToVideo(videoEl)
    }
  },
  { immediate: true }
)

onMounted(async () => {
  ibStore.isMockInterviewMode = true
  media.refreshDevicesList()

  // Prompt camera and microphone permissions automatically on mount
  try {
    const s = await media.requestPermissions()
    await nextTick()
    if (userVideo.value && s) {
      media.attachStreamToVideo(userVideo.value)
    }
    if (s) {
      audioLevel.startAnalyser(s, media.micEnabled.value)
    }
  } catch (e) {
    console.warn('Initial camera/mic setup notice:', e)
  }
  try {
    const res = await api.get('/api/resumes')
    if (res.data && res.data.length > 0) {
      const activeRes = res.data[0]
      const pInfo = activeRes.personal_info || {}
      parsedProfile.value = {
        resume_id: activeRes.id?.toString(),
        name: pInfo.name || activeRes.title || candidateName.value,
        target_role: pInfo.target_role || selectedRole.value,
        experience_level: pInfo.experience_level || 'Fresher',
        skills: activeRes.skills || [],
        projects: activeRes.projects || [],
        experience: activeRes.experience || [],
        education: activeRes.education || [],
        certifications: activeRes.certifications || []
      }
      if (pInfo.name) candidateName.value = pInfo.name
      if (pInfo.target_role) selectedRole.value = pInfo.target_role
    }
  } catch (e) {
    console.warn('Resume load warning:', e)
  }

  if (route.query.role) {
    selectedRole.value = route.query.role as string
  }
  if (route.query.type) {
    interviewType.value = route.query.type as string
  }

  await restoreActiveSessionFromQuery()
})

const restoreActiveSessionFromQuery = async () => {
  const savedActiveRaw = localStorage.getItem('active_live_interview')
  let savedActive: any = null
  try {
    if (savedActiveRaw) savedActive = JSON.parse(savedActiveRaw)
  } catch (e) {}

  const reqSessionId = (route.query.session_id as string) || (savedActive ? savedActive.session_id : null)

  if (reqSessionId || route.query.start === 'true' || savedActive) {
    const activeRole = (route.query.role as string) || (savedActive ? savedActive.role : selectedRole.value) || 'Software Engineer'
    if (activeRole) selectedRole.value = activeRole

    // Ensure parsedProfile exists so live workspace displays cleanly
    if (!parsedProfile.value) {
      parsedProfile.value = {
        resume_id: `res-${Date.now()}`,
        name: candidateName.value || 'Candidate',
        target_role: selectedRole.value,
        experience_level: 'Mid-Level',
        skills: ['Core Technical Skills', 'System Architecture', 'Problem Solving'],
        projects: [{ name: 'Primary Engineering Project' }]
      }
    }

    const sessIdToUse = reqSessionId || (savedActive ? savedActive.session_id : `sess-${Date.now()}`)

    // Always unconditionally assign activeSession so the live room workspace is GUARANTEED to render
    activeSession.value = {
      session_id: sessIdToUse,
      role: selectedRole.value,
      candidate_profile: { name: candidateName.value, target_role: selectedRole.value }
    }

    if (!localStorage.getItem('active_live_interview')) {
      localStorage.setItem('active_live_interview', JSON.stringify({
        session_id: sessIdToUse,
        role: selectedRole.value,
        started_at: new Date().toISOString()
      }))
    }

    // Re-engage camera & microphone stream for live workspace
    let s: MediaStream | null = null
    try {
      const resStream = await media.requestPermissions()
      if (resStream) s = resStream
    } catch (e) {
      console.warn('Media permission restore prompt skipped:', e)
    }

    await nextTick()
    setTimeout(() => {
      if (userVideo.value && media.stream.value) {
        media.attachStreamToVideo(userVideo.value)
      }
    }, 100)

    if (userVideo.value && media.stream.value) {
      media.attachStreamToVideo(userVideo.value)
    }
    if (media.stream.value || s) {
      audioLevel.startAnalyser(media.stream.value || s!, media.micEnabled.value)
    }

    startTimer()

    const welcomeQ = `Tell me about yourself, your background, and walk me through your key contributions for the ${selectedRole.value} role.`
    if (messages.value.length === 0) {
      const welcomeMsg = `### 🎯 Welcome to your AI Mock Interview, ${candidateName.value || 'Candidate'}!\n\nI am **${selectedInterviewerName.value}**, your ${selectedInterviewerRole.value}.\n\n👉 **"${welcomeQ}"**`
      messages.value = [{ role: 'assistant', content: welcomeMsg }]
      ibStore.setMockInterviewQuestion(welcomeQ, sessIdToUse)
      speakAIQuestion(welcomeQ)
    }
  }
}

// Watch route.fullPath so returning to live room restores session dynamically
watch(() => route.fullPath, () => {
  restoreActiveSessionFromQuery()
}, { immediate: true })

onUnmounted(() => {
  ibStore.isMockInterviewMode = false
  ibStore.detectedQuestion = ''
  ibStore.autoAnswerStatus = 'idle'
})
</script>
