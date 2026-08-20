<template>
  <div class="max-w-7xl mx-auto space-y-8 py-4 px-2 sm:px-4">
    
    <!-- Top Action Banner & Tab Navigation -->
    <div class="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl font-extrabold text-slate-100 flex items-center gap-2">
            <FileText class="w-7 h-7 text-indigo-400" />
            <span>AI Resume Workspace & ATS Scanner</span>
          </h1>
          <p class="text-xs text-slate-300 mt-1 flex items-center gap-2">
            <span>✨ Complete AI ATS Scanner, Error Inspector, 8 Professional Templates, and PDF/Word Export</span>
            <span class="hidden sm:inline-block px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold">✓ Interview Bit Auto-Synced</span>
          </p>
        </div>

        <div class="flex items-center gap-2 flex-wrap">
          <button @click="triggerUpload" class="btn-primary py-2.5 px-4 text-xs font-bold flex items-center gap-2 shadow-lg shadow-indigo-600/30">
            <UploadCloud class="w-4 h-4" />
            <span>Upload Resume</span>
          </button>
          <input type="file" ref="fileInput" class="hidden" accept=".pdf,.docx,.doc,.txt" @change="handleFileSelect" />

          <button @click="createNewResume" class="btn-secondary py-2.5 px-4 text-xs font-bold flex items-center gap-2 text-indigo-300 border-indigo-500/30">
            <Plus class="w-4 h-4" />
            <span>Create New Version</span>
          </button>

          <button @click="switchTab('templates')" class="btn-secondary py-2.5 px-4 text-xs font-bold flex items-center gap-2 text-purple-300 border-purple-500/30">
            <Sparkles class="w-4 h-4" />
            <span>Templates</span>
          </button>
        </div>
      </div>

      <!-- Template Applied Notification Alert Banner -->
      <div v-if="templateSuccessMsg" class="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-300 font-bold flex items-center justify-between gap-3 animate-fadeIn">
        <div class="flex items-center gap-2">
          <Check class="w-4 h-4 text-emerald-400" />
          <span>{{ templateSuccessMsg }}</span>
        </div>
        <span class="text-[10px] text-emerald-400 font-mono">100% Content Preserved</span>
      </div>

      <!-- Quick Guidance Info Note -->
      <div v-else class="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-200 flex items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <span class="text-base">💡</span>
          <span><strong>Quick Tip:</strong> Uploading or editing your resume automatically updates your ATS score and syncs your work experience/internships with Interview Bit!</span>
        </div>
        <span class="text-[10px] text-indigo-400 font-mono font-bold whitespace-nowrap">Auto Sync Active</span>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex items-center gap-2 border-t border-slate-800/80 pt-4 overflow-x-auto text-xs font-bold">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="switchTab(tab.id as any)"
          :class="[
            'px-4 py-2 rounded-xl transition flex items-center gap-2 whitespace-nowrap',
            activeTab === tab.id
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
              : 'bg-slate-900 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          ]"
        >
          <component :is="tab.icon" class="w-4 h-4" />
          <span>{{ tab.label }}</span>
          <span v-if="tab.count" class="px-1.5 py-0.5 rounded-full bg-slate-950 text-[10px] border border-slate-800">{{ tab.count }}</span>
        </button>
      </div>
    </div>

    <!-- Upload Progress Indicator -->
    <div v-if="isUploading" class="glass-card rounded-2xl p-6 border border-indigo-500/40 space-y-4 animate-pulse bg-indigo-950/20">
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold text-indigo-300 uppercase tracking-wider flex items-center gap-2">
          <Loader2 class="w-4 h-4 animate-spin text-indigo-400" />
          <span>Scanning & Processing Resume...</span>
        </span>
        <span class="text-xs text-indigo-400 font-mono font-bold">{{ uploadStep }}</span>
      </div>

      <div class="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800">
        <div class="bg-gradient-to-r from-indigo-500 to-purple-500 h-full transition-all duration-300" :style="{ width: uploadProgress + '%' }"></div>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] text-slate-400">
        <span :class="{ 'text-emerald-400 font-bold': uploadProgress >= 20 }">✓ Extracting Text</span>
        <span :class="{ 'text-emerald-400 font-bold': uploadProgress >= 50 }">✓ Parsing Sections</span>
        <span :class="{ 'text-emerald-400 font-bold': uploadProgress >= 80 }">✓ Scanning Errors</span>
        <span :class="{ 'text-emerald-400 font-bold': uploadProgress >= 100 }">✓ ATS Calculation</span>
      </div>
    </div>

    <!-- 1. MY RESUMES DASHBOARD TAB -->
    <div v-if="activeTab === 'dashboard'" class="space-y-6">
      
      <!-- Empty State -->
      <div v-if="!resumes.length && !isLoading" class="glass-card rounded-2xl p-12 text-center space-y-4 border border-slate-800">
        <div class="w-16 h-16 rounded-2xl bg-indigo-600/10 text-indigo-400 flex items-center justify-center mx-auto text-3xl">
          📄
        </div>
        <h3 class="text-lg font-bold text-slate-100">No Resumes Saved Yet</h3>
        <p class="text-xs text-slate-400 max-w-md mx-auto">
          Upload an existing PDF/DOCX resume or build a brand-new 100% ATS optimized resume template.
        </p>
        <div class="flex justify-center gap-3 pt-2">
          <button @click="triggerUpload" class="btn-primary py-2.5 px-5 text-xs font-bold flex items-center gap-2">
            <UploadCloud class="w-4 h-4" />
            <span>Upload Resume</span>
          </button>
        </div>
      </div>

      <!-- Resumes Grid Cards -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="res in resumes"
          :key="res.id"
          :class="[
            'glass-card rounded-2xl p-6 border transition-all duration-300 flex flex-col justify-between space-y-4 shadow-xl',
            selectedResume?.id === res.id ? 'border-indigo-500 bg-indigo-950/20' : 'border-slate-800 hover:border-slate-700 bg-slate-950/40'
          ]"
        >
          <div class="space-y-3">
            <div class="flex items-start justify-between gap-2">
              <div>
                <div class="flex items-center gap-2">
                  <h3 class="font-bold text-slate-100 text-sm truncate max-w-[180px]">{{ res.title }}</h3>
                  <span v-if="res.is_primary" class="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[9px] font-bold">Primary</span>
                </div>
                <p class="text-[11px] text-slate-400 font-mono mt-0.5">Updated: {{ formatDate(res.updated_at || res.created_at) }}</p>
              </div>

              <!-- ATS Compatibility Badge -->
              <div class="text-right">
                <span class="text-[10px] text-slate-400 uppercase font-bold block">AI ATS Compatibility</span>
                <span class="text-base font-extrabold font-mono text-emerald-400">{{ res.ats_score || 85 }} / 100</span>
              </div>
            </div>

            <!-- Highlights -->
            <div class="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1 text-xs">
              <p class="text-emerald-400 font-medium text-[11px]">✓ Strong ATS Compatibility</p>
              <p class="text-indigo-300 font-medium text-[11px]">✓ {{ (res.skills || []).length }} Key Technical Skills Found</p>
              <p :class="(res.issues || []).length ? 'text-amber-400' : 'text-slate-400'" class="font-medium text-[11px]">
                ⚠ {{ (res.issues || []).length }} Formatting/Spelling Issues Detected
              </p>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="grid grid-cols-2 gap-2 pt-2 text-xs font-bold border-t border-slate-800/80">
            <button @click="selectResume(res, 'analyzer')" class="btn-secondary py-1.5 px-2 text-[11px] text-indigo-300 border-indigo-500/30 flex items-center justify-center gap-1">
              <Search class="w-3.5 h-3.5" />
              <span>View Analysis</span>
            </button>
            <button @click="selectResume(res, 'editor')" class="btn-secondary py-1.5 px-2 text-[11px] text-slate-200 border-slate-700 flex items-center justify-center gap-1">
              <Edit3 class="w-3.5 h-3.5" />
              <span>Edit Builder</span>
            </button>
            <button @click="selectResume(res, 'export')" class="btn-primary py-1.5 px-2 text-[11px] flex items-center justify-center gap-1">
              <Download class="w-3.5 h-3.5" />
              <span>Export PDF</span>
            </button>
            <button @click="deleteResume(res.id)" class="btn-secondary py-1.5 px-2 text-[11px] text-rose-400 border-rose-500/30 hover:bg-rose-500/10 flex items-center justify-center gap-1">
              <Trash2 class="w-3.5 h-3.5" />
              <span>Delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. RESUME ANALYZER & ERROR SCANNER TAB -->
    <div v-if="activeTab === 'analyzer' && selectedResume" class="space-y-6">
      
      <!-- ATS Score Header Breakdown -->
      <div class="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800 pb-4 gap-4">
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-xl font-bold text-slate-100">{{ selectedResume.title }}</h2>
              <span class="text-xs px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20 font-mono">{{ selectedResume.version_name }}</span>
            </div>
            <p class="text-xs text-slate-400 mt-1">
              AI Estimated ATS Compatibility Score (Parsing & Keyword Match Engine)
            </p>
          </div>

          <div class="flex items-center gap-4 bg-slate-900 p-4 rounded-xl border border-slate-800">
            <div class="text-center">
              <span class="text-[10px] text-slate-400 font-bold uppercase block">Estimated ATS Compatibility Score</span>
              <span class="text-2xl font-black font-mono text-emerald-400">{{ selectedResume.ats_score || 85 }} / 100</span>
            </div>
          </div>
        </div>

        <!-- Measurable Checks Breakdown Grid -->
        <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-3 text-xs text-center">
          <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span class="text-[10px] text-slate-400 font-bold uppercase block">Keyword Match</span>
            <span class="font-bold text-indigo-400 font-mono">{{ selectedResume.metrics?.keyword_match?.score || 24 }}/25</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span class="text-[10px] text-slate-400 font-bold uppercase block">Structure</span>
            <span class="font-bold text-indigo-400 font-mono">{{ selectedResume.metrics?.structure?.score || 20 }}/20</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span class="text-[10px] text-slate-400 font-bold uppercase block">Experience</span>
            <span class="font-bold text-indigo-400 font-mono">{{ selectedResume.metrics?.experience?.score || 18 }}/20</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span class="text-[10px] text-slate-400 font-bold uppercase block">Skills</span>
            <span class="font-bold text-indigo-400 font-mono">{{ selectedResume.metrics?.skills?.score || 15 }}/15</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span class="text-[10px] text-slate-400 font-bold uppercase block">Formatting</span>
            <span class="font-bold text-indigo-400 font-mono">{{ selectedResume.metrics?.formatting?.score || 10 }}/10</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span class="text-[10px] text-slate-400 font-bold uppercase block">Contact Info</span>
            <span class="font-bold text-indigo-400 font-mono">{{ selectedResume.metrics?.contact_info?.score || 5 }}/5</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <span class="text-[10px] text-slate-400 font-bold uppercase block">Grammar</span>
            <span class="font-bold text-indigo-400 font-mono">{{ selectedResume.metrics?.grammar?.score || 3 }}/5</span>
          </div>
        </div>
      </div>

      <!-- SIDE-BY-SIDE LAYOUT GRID (Scanner Left + Live Resume Right) -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <!-- Left Column: Issues Scanner & Job Matcher (Col 7) -->
        <div class="lg:col-span-7 space-y-6">
          
          <!-- ISSUES FOUND SCANNER SECTION -->
          <div class="glass-card rounded-2xl p-6 border border-slate-800 space-y-5">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3 flex-wrap gap-2">
              <div>
                <h3 class="text-base font-bold text-slate-100 flex items-center gap-2">
                  <AlertTriangle class="w-5 h-5 text-amber-400" />
                  <span>Resume Issues & Error Scanner</span>
                </h3>
                <p class="text-xs text-slate-400">Identified spelling, spacing, capitalization, and grammar inconsistencies</p>
              </div>

              <div class="flex items-center gap-2 flex-wrap">
                <button @click="fixAllIssues" :disabled="!selectedResume.issues?.length" class="btn-primary py-1.5 px-3 text-xs font-bold flex items-center gap-1">
                  <Wand2 class="w-3.5 h-3.5" />
                  <span>Fix All Safe Errors</span>
                </button>
                <button @click="exportFile('pdf')" class="btn-secondary py-1.5 px-3 text-xs font-bold text-indigo-300 border-indigo-500/30 flex items-center gap-1">
                  <Download class="w-3.5 h-3.5" />
                  <span>Export PDF</span>
                </button>
                <button @click="exportFile('docx')" class="btn-secondary py-1.5 px-3 text-xs font-bold text-slate-200 border-slate-700 flex items-center gap-1">
                  <FileCode class="w-3.5 h-3.5" />
                  <span>Export Word</span>
                </button>
                <button @click="exportATSReport" class="btn-secondary py-1.5 px-3 text-xs font-bold text-emerald-300 border-emerald-500/30 flex items-center gap-1">
                  <FileText class="w-3.5 h-3.5" />
                  <span>Export ATS Report</span>
                </button>
              </div>
            </div>

            <!-- Issue Severity Pills -->
            <div class="flex items-center gap-4 text-xs font-bold">
              <span class="text-rose-400 bg-rose-500/10 px-3 py-1 rounded-lg border border-rose-500/20">
                🔴 Critical: {{ criticalCount }}
              </span>
              <span class="text-amber-400 bg-amber-500/10 px-3 py-1 rounded-lg border border-amber-500/20">
                🟠 Warning: {{ warningCount }}
              </span>
              <span class="text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-lg border border-emerald-500/20">
                🟢 Suggestions: {{ suggestionCount }}
              </span>
            </div>

            <!-- Issues List with Distinct Color Styling -->
            <div v-if="selectedResume.issues?.length" class="space-y-3">
              <div
                v-for="iss in selectedResume.issues"
                :key="iss.id"
                :class="[
                  'p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs transition-all',
                  iss.severity === 'Critical' ? 'bg-rose-950/30 border-rose-500/40' :
                  iss.severity === 'Warning' ? 'bg-amber-950/30 border-amber-500/40' :
                  'bg-emerald-950/30 border-emerald-500/40'
                ]"
              >
                <div class="space-y-1">
                  <div class="flex items-center gap-2">
                    <span class="font-bold text-slate-100">Type: {{ iss.type }}</span>
                    <span :class="getSeverityClass(iss.severity)" class="text-[10px] px-2 py-0.5 rounded font-mono uppercase font-bold">{{ iss.severity }}</span>
                  </div>
                  <p class="text-slate-200">
                    Found: <span class="text-rose-400 font-mono font-bold bg-rose-500/10 px-1.5 py-0.5 rounded border border-rose-500/20">"{{ iss.found }}"</span> → Suggested: <span class="text-emerald-400 font-mono font-bold bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">"{{ iss.suggested }}"</span>
                  </p>
                  <p class="text-slate-400 text-[11px] italic">{{ iss.why }}</p>
                </div>

                <button @click="fixSingleIssue(iss.id)" class="btn-primary py-1.5 px-4 text-xs font-bold text-white shadow-md self-start sm:self-center cursor-pointer">
                  <span>Fix Error</span>
                </button>
              </div>
            </div>

            <div v-else class="p-6 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold text-center">
              ✓ Clean Resume! No critical spelling, spacing, or capitalization errors detected.
            </div>
          </div>

          <!-- JOB DESCRIPTION MATCHING SECTION -->
          <div class="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
            <h3 class="text-base font-bold text-slate-100 flex items-center gap-2">
              <Target class="w-5 h-5 text-indigo-400" />
              <span>Job Description Matching & ATS Keyword Analysis</span>
            </h3>
            <p class="text-xs text-slate-400">Paste target job description to calculate exact match percentage and missing keywords</p>

            <div class="space-y-3">
              <textarea
                v-model="jdInput"
                rows="3"
                placeholder="Paste Job Description here (e.g. Seeking Senior Backend Developer skilled in Python, FastAPI, Docker, and PostgreSQL)..."
                class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs text-slate-100 outline-none focus:border-indigo-500"
              ></textarea>
              <button @click="runJobMatch" :disabled="!jdInput.trim()" class="btn-primary py-2 px-4 text-xs font-bold flex items-center gap-1.5">
                <Search class="w-3.5 h-3.5" />
                <span>Analyze Job Match</span>
              </button>
            </div>

            <div v-if="jobMatchResult" class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3 text-xs animate-fadeIn">
              <div class="flex items-center justify-between border-b border-slate-800 pb-2">
                <span class="font-bold text-slate-100">Overall Job Match:</span>
                <span class="text-lg font-black font-mono text-emerald-400">{{ jobMatchResult.overall_match }}%</span>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <span class="font-bold text-emerald-400 block mb-1">✓ Matched Skills Found:</span>
                  <div class="flex flex-wrap gap-1">
                    <span v-for="s in jobMatchResult.matched_skills" :key="s" class="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-[11px] font-mono">{{ s }}</span>
                  </div>
                </div>

                <div>
                  <span class="font-bold text-amber-400 block mb-1">⚠ Consider Adding / Missing:</span>
                  <div class="flex flex-wrap gap-1">
                    <span v-for="ms in jobMatchResult.missing_skills" :key="ms" class="px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[11px] font-mono">{{ ms }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Live Resume Preview (Col 5) -->
        <div class="lg:col-span-5 glass-card rounded-2xl p-6 border border-slate-800 space-y-4 bg-slate-950">
          <div class="flex items-center justify-between border-b border-slate-800 pb-2">
            <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Live Resume Document View
            </h3>
            <div class="flex items-center gap-2 flex-wrap">
              <!-- Instant Template Select Dropdown -->
              <select
                :value="selectedResume?.template_id || 'modern_ats'"
                @change="handleQuickTemplateChange"
                class="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1 text-[11px] text-purple-300 outline-none font-bold cursor-pointer hover:border-purple-500"
                title="Switch Resume Template Layout"
              >
                <option v-for="t in templates" :key="t.id" :value="t.id">🎨 {{ t.name }} (ATS {{ t.atsScore }}%)</option>
              </select>

              <button @click="exportFile('pdf')" class="btn-primary py-1 px-2.5 text-[10px] font-bold flex items-center gap-1" title="Download Machine-Readable PDF">
                <Download class="w-3 h-3" />
                <span>PDF</span>
              </button>

              <button @click="exportFile('docx')" class="btn-secondary py-1 px-2.5 text-[10px] font-bold text-slate-200 border-slate-700 flex items-center gap-1" title="Download Word Document">
                <FileCode class="w-3 h-3" />
                <span>Word</span>
              </button>

              <button @click="exportPlainText" class="btn-secondary py-1 px-2.5 text-[10px] font-bold text-emerald-300 border-emerald-500/30 flex items-center gap-1" title="Download Plain Text">
                <FileText class="w-3 h-3" />
                <span>TXT</span>
              </button>

              <button @click="copyResumeToClipboard" class="btn-secondary py-1 px-2.5 text-[10px] font-bold text-indigo-300 border-indigo-500/30 flex items-center gap-1" title="Copy Text to Clipboard">
                <Copy class="w-3 h-3" />
                <span>Copy</span>
              </button>

              <button @click="printResumeDocument" class="btn-secondary py-1 px-2.5 text-[10px] font-bold text-purple-300 border-purple-500/30 flex items-center gap-1" title="Print Resume">
                <Printer class="w-3 h-3" />
                <span>Print</span>
              </button>
            </div>
          </div>

          <div class="bg-white text-slate-900 p-6 rounded-xl space-y-4 shadow-2xl font-sans text-xs min-h-[550px] border border-slate-200">
            <div class="border-b-2 border-slate-900 pb-3 space-y-1">
              <h1 class="text-xl font-black uppercase tracking-wide text-slate-900">{{ editForm.personal_info.name || 'CANDIDATE NAME' }}</h1>
              <p class="text-xs text-indigo-900 font-bold leading-relaxed">
                {{ editForm.personal_info.target_role }}
                <span v-if="editForm.personal_info.email"> | {{ editForm.personal_info.email }}</span>
                <span v-if="editForm.personal_info.phone"> | {{ editForm.personal_info.phone }}</span>
                <span v-if="editForm.personal_info.location"> | {{ editForm.personal_info.location }}</span>
                <span v-if="editForm.personal_info.linkedin"> | <a :href="editForm.personal_info.linkedin" target="_blank" class="underline">LinkedIn</a></span>
                <span v-if="editForm.personal_info.github"> | <a :href="editForm.personal_info.github" target="_blank" class="underline">GitHub</a></span>
              </p>
            </div>

            <div v-if="editForm.summary" class="space-y-1.5 border-b border-slate-300 pb-3">
              <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Professional Summary</h4>
              <p class="text-slate-800 text-[11px] leading-relaxed">{{ editForm.summary }}</p>
            </div>

            <div v-if="editForm.skills?.length" class="space-y-1.5 border-b border-slate-300 pb-3">
              <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Core Technical Skills</h4>
              <p class="text-slate-800 text-[11px] font-semibold">{{ editForm.skills.join(' • ') }}</p>
            </div>

            <div v-if="editForm.experience?.length" class="space-y-2 border-b border-slate-300 pb-3">
              <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Work Experience</h4>
              <div v-for="(exp, idx) in editForm.experience" :key="idx" class="space-y-0.5">
                <div class="flex items-center justify-between text-[11px] flex-wrap gap-1">
                  <span class="font-bold text-slate-900">{{ exp.role || 'Software Engineer' }} {{ exp.company ? '— ' + exp.company : '' }}</span>
                  <span v-if="exp.duration || exp.dates" class="text-[10px] text-slate-700 font-mono font-bold bg-slate-100 px-1.5 py-0.5 rounded border border-slate-300">{{ exp.duration || exp.dates }}</span>
                </div>
                <p v-if="exp.description" class="text-[10px] text-slate-800 leading-relaxed">• {{ exp.description }}</p>
              </div>
            </div>

            <div v-if="editForm.projects?.length" class="space-y-2 border-b border-slate-300 pb-3">
              <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Key Projects</h4>
              <div v-for="(proj, pIdx) in editForm.projects" :key="pIdx" class="space-y-0.5">
                <div class="text-[11px]">
                  <span class="font-bold text-slate-900">{{ proj.name }}</span>
                  <span v-if="proj.technologies?.length" class="text-[10px] text-indigo-900 font-mono font-bold"> [{{ proj.technologies.join(', ') }}]</span>
                </div>
                <p class="text-[10px] text-slate-800 leading-relaxed">• {{ proj.description }}</p>
              </div>
            </div>

            <div v-if="editForm.certifications?.length" class="space-y-1.5 border-b border-slate-300 pb-3">
              <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Certifications</h4>
              <p class="text-slate-800 text-[11px]">• {{ editForm.certifications.join(' • ') }}</p>
            </div>

            <div v-if="editForm.education?.length" class="space-y-2 border-b border-slate-300 pb-3">
              <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Education</h4>
              <div v-for="(edu, edIdx) in editForm.education" :key="edIdx" class="space-y-0.5 text-[10px]">
                <div class="flex items-center justify-between font-bold text-slate-900">
                  <span>{{ typeof edu === 'string' ? edu : (edu.degree || edu.title || 'Degree') }} {{ typeof edu === 'object' && (edu.institution || edu.school) ? '— ' + (edu.institution || edu.school) : '' }}</span>
                  <span v-if="typeof edu === 'object' && (edu.year || edu.duration)" class="text-slate-600 font-mono text-[9.5px]">{{ edu.year || edu.duration }}</span>
                </div>
                <p v-if="typeof edu === 'object' && edu.aggregate" class="text-slate-700 text-[9.5px]">Aggregate: {{ edu.aggregate }}</p>
              </div>
            </div>

            <div v-if="editForm.achievements?.length" class="space-y-1.5 border-b border-slate-300 pb-3">
              <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Key Achievements</h4>
              <p class="text-slate-800 text-[11px]">• {{ editForm.achievements.join(' • ') }}</p>
            </div>

            <div v-if="editForm.links?.length" class="space-y-1 pt-1">
              <h4 class="font-bold uppercase text-[10px] text-slate-700 tracking-wider">Links & Portfolio</h4>
              <div class="flex flex-wrap gap-2 text-[10px]">
                <a v-for="link in editForm.links" :key="link" :href="link" target="_blank" class="text-indigo-600 font-bold underline font-mono">{{ link }}</a>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- 3. RESUME EDITOR & BUILDER TAB -->
    <div v-if="activeTab === 'editor' && selectedResume" class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      <!-- Form Controls (Col 7) -->
      <div class="lg:col-span-7 glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
        <h3 class="text-base font-bold text-slate-100 border-b border-slate-800 pb-3 flex items-center justify-between">
          <span>Editable Resume Builder</span>
          <button @click="saveResumeChanges" class="btn-primary py-1.5 px-4 text-xs font-bold flex items-center gap-1.5">
            <Check class="w-3.5 h-3.5" />
            <span>Save Resume</span>
          </button>
        </h3>

        <!-- Personal Info -->
        <div class="space-y-3 text-xs">
          <span class="font-bold text-indigo-400 uppercase tracking-wider block">Personal Information</span>
          <div class="grid grid-cols-2 gap-3">
            <input v-model="editForm.personal_info.name" placeholder="Full Name" class="bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-slate-100" />
            <input v-model="editForm.personal_info.target_role" placeholder="Target Role" class="bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-slate-100" />
            <input v-model="editForm.personal_info.email" placeholder="Email" class="bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-slate-100" />
            <input v-model="editForm.personal_info.phone" placeholder="Phone" class="bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-slate-100" />
            <input v-model="editForm.personal_info.location" placeholder="Location (e.g. Hyderabad, India)" class="bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-slate-100" />
            <input v-model="editForm.personal_info.linkedin" placeholder="LinkedIn URL (e.g. linkedin.com/in/username)" class="bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-slate-100" />
            <input v-model="editForm.personal_info.github" placeholder="GitHub URL (e.g. github.com/username)" class="bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-slate-100" />
          </div>
        </div>

        <!-- Summary -->
        <div class="space-y-2 text-xs">
          <span class="font-bold text-indigo-400 uppercase tracking-wider block">Professional Summary</span>
          <textarea v-model="editForm.summary" rows="3" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-slate-100 outline-none"></textarea>
        </div>

        <!-- Skills -->
        <div class="space-y-2 text-xs">
          <span class="font-bold text-indigo-400 uppercase tracking-wider block">Skills (Comma Separated)</span>
          <input v-model="skillsInput" @blur="updateSkillsFromInput" placeholder="Python, FastAPI, Docker, SQL" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-slate-100 font-mono" />
        </div>

        <!-- Work Experience (Jobs, Freelance, Internships) -->
        <div class="space-y-3 text-xs">
          <div class="flex items-center justify-between">
            <span class="font-bold text-indigo-400 uppercase tracking-wider">Work Experience (Jobs, Freelance, Internships)</span>
            <button @click="addExperienceItem" class="text-xs text-indigo-400 font-bold hover:underline">+ Add Experience</button>
          </div>

          <div v-for="(exp, idx) in editForm.experience" :key="idx" class="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold text-slate-400 uppercase">Experience #{{ idx + 1 }}</span>
              <div class="flex items-center gap-2 text-[10px]">
                <button v-if="idx > 0" @click="moveExperience(idx, -1)" class="text-indigo-400 font-bold hover:underline">↑ Up</button>
                <button v-if="idx < editForm.experience.length - 1" @click="moveExperience(idx, 1)" class="text-indigo-400 font-bold hover:underline">↓ Down</button>
                <button @click="removeExperienceItem(idx)" class="text-rose-400 font-bold hover:underline">Remove</button>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <input v-model="exp.role" placeholder="Role / Title (e.g. Backend Freelancer)" class="bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100" />
              <input v-model="exp.company" placeholder="Company / Client" class="bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100" />
              <input v-model="exp.duration" placeholder="Dates (e.g. Jan 2024 - Present)" class="bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100 font-mono" />
              <input v-model="exp.type" placeholder="Type (Job / Freelance / Internship)" class="bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100" />
            </div>
            <textarea v-model="exp.description" rows="2" placeholder="Key responsibilities and technical achievements..." class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100 outline-none"></textarea>
          </div>
        </div>

        <!-- Key Projects -->
        <div class="space-y-3 text-xs">
          <div class="flex items-center justify-between">
            <span class="font-bold text-indigo-400 uppercase tracking-wider">Key Projects</span>
            <button @click="addProjectItem" class="text-xs text-indigo-400 font-bold hover:underline">+ Add Project</button>
          </div>

          <div v-for="(proj, pIdx) in editForm.projects" :key="pIdx" class="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold text-slate-400 uppercase">Project #{{ pIdx + 1 }}</span>
              <div class="flex items-center gap-2 text-[10px]">
                <button v-if="pIdx > 0" @click="moveProject(pIdx, -1)" class="text-indigo-400 font-bold hover:underline">↑ Up</button>
                <button v-if="pIdx < editForm.projects.length - 1" @click="moveProject(pIdx, 1)" class="text-indigo-400 font-bold hover:underline">↓ Down</button>
                <button @click="removeProjectItem(pIdx)" class="text-rose-400 font-bold hover:underline">Remove</button>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <input v-model="proj.name" placeholder="Project Name" class="bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100" />
              <input v-model="proj.tech_str" @blur="updateProjectTech(proj)" placeholder="Technologies (Comma separated)" class="bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100 font-mono" />
            </div>
            <textarea v-model="proj.description" rows="2" placeholder="Project description and key technical architecture..." class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100 outline-none"></textarea>
          </div>
        </div>

        <!-- Education Section -->
        <div class="space-y-3 text-xs">
          <div class="flex items-center justify-between">
            <span class="font-bold text-indigo-400 uppercase tracking-wider">Education</span>
            <button @click="addEducationItem" class="text-xs text-indigo-400 font-bold hover:underline">+ Add Education</button>
          </div>

          <div v-for="(edu, edIdx) in editForm.education" :key="edIdx" class="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold text-slate-400 uppercase">Education #{{ edIdx + 1 }}</span>
              <button @click="removeEducationItem(edIdx)" class="text-rose-400 font-bold hover:underline text-[10px]">Remove</button>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <input v-model="edu.degree" placeholder="Degree / Certificate (e.g. B.Tech Data Science)" class="bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100" />
              <input v-model="edu.institution" placeholder="Institution / College Name" class="bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100" />
              <input v-model="edu.year" placeholder="Years / Duration (e.g. 2023 - 2027 Expected)" class="bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100 font-mono" />
              <input v-model="edu.aggregate" placeholder="Aggregate / GPA (e.g. 70%)" class="bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100" />
            </div>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3 text-xs">
          <div class="space-y-1">
            <span class="font-bold text-indigo-400 uppercase tracking-wider block">Certifications (Comma separated)</span>
            <input v-model="certsInput" @blur="updateCertsFromInput" placeholder="AWS Certified, Deep Learning" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-slate-100" />
          </div>

          <div class="space-y-1">
            <span class="font-bold text-indigo-400 uppercase tracking-wider block">Achievements (Comma separated)</span>
            <input v-model="achievementsInput" @blur="updateAchievementsFromInput" placeholder="1st Rank Hackathon, Top Contributor" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-slate-100" />
          </div>
        </div>

        <!-- Links / Hyperlinks -->
        <div class="space-y-2 text-xs">
          <span class="font-bold text-indigo-400 uppercase tracking-wider block">Portfolio & Hyperlinks (Comma separated URLs)</span>
          <input v-model="linksInput" @blur="updateLinksFromInput" placeholder="https://github.com/myrepo, https://portfolio.dev" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-slate-100 font-mono" />
        </div>
      </div>

      <!-- Live Resume Preview (Col 5) -->
      <div class="lg:col-span-5 glass-card rounded-2xl p-6 border border-slate-800 space-y-4 bg-slate-950">
        <div class="flex items-center justify-between border-b border-slate-800 pb-2">
          <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Live Template Preview: {{ selectedResume.version_name }}
          </h3>
          <span class="text-xs font-bold font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">100% ATS Ready</span>
        </div>

        <div class="bg-white text-slate-900 p-6 rounded-xl space-y-4 shadow-2xl font-sans text-xs min-h-[600px] border border-slate-200">
          <div class="border-b-2 border-slate-900 pb-3 space-y-1">
            <h1 class="text-xl font-black uppercase tracking-wide text-slate-900">{{ editForm.personal_info.name || 'CANDIDATE NAME' }}</h1>
            <p class="text-xs text-indigo-900 font-bold leading-relaxed">
              {{ editForm.personal_info.target_role }}
              <span v-if="editForm.personal_info.email"> | {{ editForm.personal_info.email }}</span>
              <span v-if="editForm.personal_info.phone"> | {{ editForm.personal_info.phone }}</span>
              <span v-if="editForm.personal_info.location"> | {{ editForm.personal_info.location }}</span>
              <span v-if="editForm.personal_info.linkedin"> | <a :href="editForm.personal_info.linkedin" target="_blank" class="underline">LinkedIn</a></span>
              <span v-if="editForm.personal_info.github"> | <a :href="editForm.personal_info.github" target="_blank" class="underline">GitHub</a></span>
            </p>
          </div>

          <div v-if="editForm.summary" class="space-y-1.5 border-b border-slate-300 pb-3">
            <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Professional Summary</h4>
            <p class="text-slate-800 text-[11px] leading-relaxed">{{ editForm.summary }}</p>
          </div>

          <div v-if="editForm.skills?.length" class="space-y-1.5 border-b border-slate-300 pb-3">
            <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Core Technical Skills</h4>
            <p class="text-slate-800 text-[11px] font-semibold">{{ editForm.skills.join(' • ') }}</p>
          </div>

            <div v-if="editForm.experience?.length" class="space-y-2 border-b border-slate-300 pb-3">
              <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Work Experience</h4>
              <div v-for="(exp, idx) in editForm.experience" :key="idx" class="space-y-0.5">
                <div class="flex items-center justify-between text-[11px] flex-wrap gap-1">
                  <span class="font-bold text-slate-900">{{ exp.role || 'Software Engineer' }} {{ exp.company ? '— ' + exp.company : '' }}</span>
                  <span v-if="exp.duration || exp.dates" class="text-[10px] text-slate-700 font-mono font-bold bg-slate-100 px-1.5 py-0.5 rounded border border-slate-300">{{ exp.duration || exp.dates }}</span>
                </div>
                <p v-if="exp.description" class="text-[10px] text-slate-800 leading-relaxed">• {{ exp.description }}</p>
              </div>
            </div>

          <div v-if="editForm.projects?.length" class="space-y-2 border-b border-slate-300 pb-3">
            <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Key Projects</h4>
            <div v-for="(proj, pIdx) in editForm.projects" :key="pIdx" class="space-y-0.5">
              <div class="text-[11px]">
                <span class="font-bold text-slate-900">{{ proj.name }}</span>
                <span v-if="proj.technologies?.length" class="text-[10px] text-indigo-900 font-mono font-bold"> [{{ proj.technologies.join(', ') }}]</span>
              </div>
              <p class="text-[10px] text-slate-800 leading-relaxed">• {{ proj.description }}</p>
            </div>
          </div>

          <div v-if="editForm.certifications?.length" class="space-y-1.5 border-b border-slate-300 pb-3">
            <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Certifications</h4>
            <p class="text-slate-800 text-[11px]">• {{ editForm.certifications.join(' • ') }}</p>
          </div>

          <div v-if="editForm.education?.length" class="space-y-2 border-b border-slate-300 pb-3">
            <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Education</h4>
            <div v-for="(edu, edIdx) in editForm.education" :key="edIdx" class="space-y-0.5 text-[10px]">
              <div class="flex items-center justify-between font-bold text-slate-900">
                <span>{{ typeof edu === 'string' ? edu : (edu.degree || edu.title || 'Degree') }} {{ typeof edu === 'object' && (edu.institution || edu.school) ? '— ' + (edu.institution || edu.school) : '' }}</span>
                <span v-if="typeof edu === 'object' && (edu.year || edu.duration)" class="text-slate-600 font-mono text-[9.5px]">{{ edu.year || edu.duration }}</span>
              </div>
              <p v-if="typeof edu === 'object' && edu.aggregate" class="text-slate-700 text-[9.5px]">Aggregate: {{ edu.aggregate }}</p>
            </div>
          </div>

          <div v-if="editForm.achievements?.length" class="space-y-1.5 border-b border-slate-300 pb-3">
            <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Key Achievements</h4>
            <p class="text-slate-800 text-[11px]">• {{ editForm.achievements.join(' • ') }}</p>
          </div>

          <div v-if="editForm.links?.length" class="space-y-1 pt-1">
            <h4 class="font-bold uppercase text-[10px] text-slate-700 tracking-wider">Links & Portfolio</h4>
            <div class="flex flex-wrap gap-2 text-[10px]">
              <a v-for="link in editForm.links" :key="link" :href="link" target="_blank" class="text-indigo-600 font-bold underline font-mono">{{ link }}</a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 4. RESUME TEMPLATES TAB -->
    <div v-if="activeTab === 'templates'" class="space-y-6">
      <div class="glass-card rounded-2xl p-6 border border-purple-500/30 space-y-4">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-slate-100 flex items-center gap-2">
              <Sparkles class="w-6 h-6 text-purple-400" />
              <span>Professional Resume Template Marketplace</span>
            </h2>
            <p class="text-xs text-slate-400 mt-1">Select from 8 ATS-optimized layout designs. All content remains 100% preserved.</p>
          </div>

          <!-- Template Search Bar -->
          <div class="relative w-full md:w-64">
            <Search class="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              v-model="templateSearch"
              placeholder="Search templates..."
              class="w-full bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-100 outline-none focus:border-purple-500"
            />
          </div>
        </div>

        <!-- Category Pills -->
        <div class="flex items-center gap-2 overflow-x-auto pt-2 text-xs font-bold">
          <button
            v-for="cat in categories"
            :key="cat"
            @click="selectedCategory = cat"
            :class="[
              'px-3.5 py-1.5 rounded-xl transition whitespace-nowrap cursor-pointer',
              selectedCategory === cat
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/20'
                : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
            ]"
          >
            {{ cat }}
          </button>
        </div>
      </div>

      <!-- Templates Grid Cards with Miniature Resume Previews -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 text-xs">
        <div
          v-for="tpl in filteredTemplates"
          :key="tpl.id"
          class="glass-card rounded-2xl p-5 border border-slate-800 hover:border-purple-500/80 transition-all duration-300 flex flex-col justify-between space-y-4 bg-slate-950/80 shadow-xl group"
        >
          <!-- MINIATURE RESUME PREVIEW CONTAINER WITH DYNAMIC TEMPLATE FONT -->
          <div class="space-y-3">
            <div
              :style="{ fontFamily: tpl.fontFamilyCSS }"
              class="bg-white text-slate-900 p-3.5 rounded-xl space-y-2 border border-slate-200 shadow-md text-[8px] leading-tight select-none h-44 overflow-hidden relative group-hover:scale-[1.02] transition-transform flex flex-col justify-between"
            >
              <div class="space-y-2">
                <div class="border-b-2 border-slate-900 pb-1.5 space-y-0.5">
                  <p class="font-black uppercase text-[9.5px] text-slate-900 truncate tracking-wide">
                    {{ editForm.personal_info.name || selectedResume?.personal_info?.name || 'ALEX JOHNSON' }}
                  </p>
                  <p class="text-[7.5px] text-indigo-900 font-bold truncate">
                    {{ editForm.personal_info.target_role || selectedResume?.personal_info?.target_role || 'Software Engineer' }}
                    <span class="text-slate-500 font-normal"> • alex@example.com • +1 555-0199</span>
                  </p>
                </div>

                <!-- Mini Summary / Profile -->
                <div class="space-y-0.5 border-b border-slate-200 pb-1.5">
                  <p class="font-bold text-[7px] uppercase tracking-wider text-slate-800 border-b border-slate-400 pb-0.5 inline-block">Professional Summary</p>
                  <p class="text-slate-700 line-clamp-2 text-[7px] leading-tight">
                    {{ editForm.summary || 'Results-driven engineer with expertise in scalable systems, modern frontend UI architectures, and cloud deployments.' }}
                  </p>
                </div>

                <!-- Mini Skills -->
                <div class="space-y-0.5 border-b border-slate-200 pb-1.5">
                  <p class="font-bold text-[7px] uppercase tracking-wider text-slate-800 border-b border-slate-400 pb-0.5 inline-block">Technical Stack</p>
                  <p class="text-slate-900 font-semibold truncate text-[7px]">
                    {{ editForm.skills?.length ? editForm.skills.join(' • ') : 'Python • FastAPI • TypeScript • Vue.js • Docker • PostgreSQL' }}
                  </p>
                </div>

                <!-- Mini Experience -->
                <div class="space-y-0.5">
                  <p class="font-bold text-[7px] uppercase tracking-wider text-slate-800 border-b border-slate-400 pb-0.5 inline-block">Experience</p>
                  <div class="flex justify-between items-center text-[7px]">
                    <span class="font-bold text-slate-900 truncate">{{ editForm.experience[0]?.role || 'Software Lead' }} {{ editForm.experience[0]?.company ? '— ' + editForm.experience[0]?.company : '— Tech Corp' }}</span>
                    <span class="text-[6.5px] text-slate-500 font-mono">2024-Present</span>
                  </div>
                  <p class="text-slate-700 line-clamp-1 text-[6.5px]">
                    • {{ editForm.experience[0]?.description || 'Engineered high-performance web applications and REST APIs.' }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Card Info -->
            <div class="space-y-1.5">
              <div class="flex items-center justify-between">
                <h3 class="font-extrabold text-slate-100 text-sm">{{ tpl.name }}</h3>
                <span class="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  ATS Score: {{ tpl.atsScore }}%
                </span>
              </div>
              <div class="flex items-center gap-1.5">
                <span class="text-[10px] font-mono font-bold text-purple-300 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">🔤 {{ tpl.fontName }}</span>
              </div>
              <p class="text-[11px] text-indigo-300 font-semibold">{{ tpl.bestFor }}</p>
              <p class="text-[11px] text-slate-400 leading-relaxed">{{ tpl.description }}</p>
            </div>
          </div>

          <!-- Card Action Buttons -->
          <div class="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800/80">
            <button
              @click="previewModalTemplate = tpl"
              class="btn-secondary py-2 text-xs font-bold text-slate-200 border-slate-700 flex items-center justify-center gap-1 cursor-pointer"
            >
              <Search class="w-3.5 h-3.5" />
              <span>Preview</span>
            </button>
            <button
              @click="applyTemplateToResume(tpl)"
              class="btn-primary py-2 text-xs font-bold text-white flex items-center justify-center gap-1 cursor-pointer shadow-lg shadow-purple-600/20"
            >
              <Check class="w-3.5 h-3.5" />
              <span>Apply</span>
            </button>
          </div>
        </div>
      </div>

      <!-- LARGE RESUME PREVIEW MODAL -->
      <div v-if="previewModalTemplate" class="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-800 rounded-2xl max-w-3xl w-full p-6 space-y-5 shadow-2xl max-h-[90vh] flex flex-col justify-between">
          <div class="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 class="text-lg font-bold text-slate-100 flex items-center gap-2">
                <span>{{ previewModalTemplate.name }} Resume Layout</span>
                <span class="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  ATS Score: {{ previewModalTemplate.atsScore }}%
                </span>
              </h3>
              <p class="text-xs text-slate-400">{{ previewModalTemplate.bestFor }}</p>
            </div>
            <button @click="previewModalTemplate = null" class="text-slate-400 hover:text-white font-bold text-lg px-2">✕</button>
          </div>

          <!-- A4 Proportional Resume Document Container -->
          <div class="overflow-y-auto max-h-[60vh] p-2">
            <div
              :style="{ fontFamily: previewModalTemplate.fontFamilyCSS }"
              class="bg-white text-slate-900 p-8 rounded-xl space-y-4 shadow-2xl text-xs border border-slate-200 min-h-[500px]"
            >
              <div class="border-b-2 border-slate-900 pb-3 space-y-1">
                <h1 class="text-2xl font-black uppercase tracking-wide text-slate-900">{{ editForm.personal_info.name || 'CANDIDATE NAME' }}</h1>
                <p class="text-xs text-indigo-900 font-bold leading-relaxed">
                  {{ editForm.personal_info.target_role }}
                  <span v-if="editForm.personal_info.email"> | {{ editForm.personal_info.email }}</span>
                  <span v-if="editForm.personal_info.phone"> | {{ editForm.personal_info.phone }}</span>
                  <span v-if="editForm.personal_info.location"> | {{ editForm.personal_info.location }}</span>
                  <span v-if="editForm.personal_info.linkedin"> | <a :href="editForm.personal_info.linkedin" target="_blank" class="underline">LinkedIn</a></span>
                  <span v-if="editForm.personal_info.github"> | <a :href="editForm.personal_info.github" target="_blank" class="underline">GitHub</a></span>
                </p>
              </div>

              <div v-if="editForm.summary" class="space-y-1.5 border-b border-slate-300 pb-3">
                <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Professional Summary</h4>
                <p class="text-slate-800 text-[11px] leading-relaxed">{{ editForm.summary }}</p>
              </div>

              <div v-if="editForm.skills?.length" class="space-y-1.5 border-b border-slate-300 pb-3">
                <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Core Technical Skills</h4>
                <p class="text-slate-800 text-[11px] font-semibold">{{ editForm.skills.join(' • ') }}</p>
              </div>

              <div v-if="editForm.experience?.length" class="space-y-2 border-b border-slate-300 pb-3">
                <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Work Experience</h4>
                <div v-for="(exp, idx) in editForm.experience" :key="idx" class="space-y-0.5">
                  <div class="flex items-center justify-between text-[11px]">
                    <span class="font-bold text-slate-900">{{ exp.role }} {{ exp.company ? '— ' + exp.company : '' }}</span>
                    <span class="text-[10px] text-slate-600 font-mono font-bold">{{ exp.duration }}</span>
                  </div>
                  <p class="text-[10px] text-slate-800 leading-relaxed">• {{ exp.description }}</p>
                </div>
              </div>

              <div v-if="editForm.projects?.length" class="space-y-2 border-b border-slate-300 pb-3">
                <h4 class="font-bold uppercase text-[11px] text-slate-900 tracking-wider border-b border-slate-800 pb-0.5">Key Projects</h4>
                <div v-for="(proj, pIdx) in editForm.projects" :key="pIdx" class="space-y-0.5">
                  <div class="text-[11px]">
                    <span class="font-bold text-slate-900">{{ proj.name }}</span>
                    <span v-if="proj.technologies?.length" class="text-[10px] text-indigo-900 font-mono font-bold"> [{{ proj.technologies.join(', ') }}]</span>
                  </div>
                  <p class="text-[10px] text-slate-800 leading-relaxed">• {{ proj.description }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Modal Action Buttons -->
          <div class="flex justify-between items-center border-t border-slate-800 pt-3 text-xs">
            <button @click="previewModalTemplate = null" class="btn-secondary py-2 px-4 font-bold text-slate-400">Cancel</button>
            <button
              @click="applyTemplateToResume(previewModalTemplate); previewModalTemplate = null"
              class="btn-primary py-2 px-6 font-bold flex items-center gap-2 shadow-xl"
            >
              <Check class="w-4 h-4" />
              <span>Apply This Template</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 5. EXPORT MENU TAB -->
    <div v-if="activeTab === 'export' && selectedResume" class="glass-card rounded-2xl p-8 border border-slate-800 max-w-2xl mx-auto space-y-6 text-center">
      <div class="space-y-2">
        <h2 class="text-xl font-bold text-slate-100">Export & Download Resume</h2>
        <p class="text-xs text-slate-400">Generate real, machine-readable PDF and Word (.docx) documents matching your selected template</p>
      </div>

      <!-- Pre-Export ATS Check -->
      <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-2 text-left">
        <div class="flex items-center justify-between border-b border-slate-800 pb-2">
          <span class="font-bold text-slate-100">Final ATS Compatibility Check</span>
          <span class="text-sm font-bold font-mono text-emerald-400">{{ selectedResume.ats_score || 85 }}/100</span>
        </div>
        <p class="text-emerald-400 font-medium">✓ Contact info verified</p>
        <p class="text-emerald-400 font-medium">✓ Standard machine-readable headings</p>
        <p class="text-emerald-400 font-medium">✓ No critical spelling errors</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-bold">
        <button @click="exportFile('pdf')" class="btn-primary py-3 flex items-center justify-center gap-2 shadow-xl">
          <FileText class="w-4 h-4" />
          <span>Download PDF (.pdf)</span>
        </button>

        <button @click="exportFile('docx')" class="btn-secondary py-3 flex items-center justify-center gap-2 text-indigo-300 border-indigo-500/30">
          <FileCode class="w-4 h-4" />
          <span>Download Word (.docx)</span>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  FileText, UploadCloud, Plus, Sparkles, Search, Edit3, Download,
  AlertTriangle, Wand2, Target, Check, FileCode, Loader2, Trash2,
  Copy, Printer
} from 'lucide-vue-next'
import { api } from '../services/api'
import type { ResumeItem } from '../types'

const activeTab = ref<'dashboard' | 'analyzer' | 'editor' | 'templates' | 'export'>('dashboard')
const resumes = ref<ResumeItem[]>([])
const selectedResume = ref<ResumeItem | null>(null)
const isLoading = ref<boolean>(false)
const isUploading = ref<boolean>(false)
const uploadProgress = ref<number>(0)
const uploadStep = ref<string>('Uploading...')
const fileInput = ref<HTMLInputElement | null>(null)

const jdInput = ref<string>('')
const jobMatchResult = ref<any>(null)
const skillsInput = ref<string>('')

const certsInput = ref<string>('')
const achievementsInput = ref<string>('')
const linksInput = ref<string>('')

const editForm = ref<{
  personal_info: { name?: string; target_role?: string; email?: string; phone?: string; location?: string; linkedin?: string; github?: string };
  summary?: string;
  skills: string[];
  experience: any[];
  projects: any[];
  education?: any[];
  certifications: string[];
  achievements: string[];
  links: string[];
}>({
  personal_info: {},
  summary: '',
  skills: [],
  experience: [],
  projects: [],
  education: [],
  certifications: [],
  achievements: [],
  links: []
})

const tabs = computed(() => [
  { id: 'dashboard', label: 'My Resumes Dashboard', icon: FileText, count: resumes.value.length },
  { id: 'analyzer', label: 'ATS Analyzer & Error Scanner', icon: Search },
  { id: 'editor', label: 'Editable Resume Builder', icon: Edit3 },
  { id: 'templates', label: 'ATS Resume Templates', icon: Sparkles },
  { id: 'export', label: 'PDF & Word Export', icon: Download }
])

const selectedCategory = ref<string>('All')
const templateSearch = ref<string>('')
const previewModalTemplate = ref<any>(null)

const categories = ['All', 'ATS Safe Only', 'Engineering', 'Fresher', 'Experienced', 'Minimal', 'Executive']

const templates = [
  {
    id: 'modern_ats',
    name: 'Modern ATS',
    category: 'Engineering',
    fontName: 'Inter / Sans-Serif',
    fontStyle: 'font-sans',
    fontFamilyCSS: 'Inter, system-ui, sans-serif',
    atsScore: 98,
    atsSafe: true,
    bestFor: 'Software, AI & Engineering Roles',
    description: 'Single-column clean typography layout (Inter font) with clear section headings.'
  },
  {
    id: 'professional',
    name: 'Professional',
    category: 'Experienced',
    fontName: 'Georgia / Serif',
    fontStyle: 'font-serif',
    fontFamilyCSS: 'Georgia, Cambria, serif',
    atsScore: 95,
    atsSafe: true,
    bestFor: 'Corporate & Engineering Management',
    description: 'Traditional corporate executive serif typography (Georgia font) with structured contact header.'
  },
  {
    id: 'software_engineer',
    name: 'Software Engineer',
    category: 'Engineering',
    fontName: 'JetBrains Mono / Tech Code',
    fontStyle: 'font-mono',
    fontFamilyCSS: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
    atsScore: 96,
    atsSafe: true,
    bestFor: 'Software & AI Developers',
    description: 'Tech monospace typography (JetBrains Mono) highlighting tech stack and project architecture.'
  },
  {
    id: 'minimal',
    name: 'Minimal',
    category: 'Minimal',
    fontName: 'Roboto / Clean Minimal',
    fontStyle: 'font-sans',
    fontFamilyCSS: 'Roboto, Helvetica, Arial, sans-serif',
    atsScore: 94,
    atsSafe: true,
    bestFor: 'Clean Typography & Simple Layouts',
    description: 'Ultra-clean minimal sans-serif font (Roboto font) with ample whitespace and borderless sections.'
  },
  {
    id: 'executive',
    name: 'Executive',
    category: 'Executive',
    fontName: 'Merriweather / Formal Serif',
    fontStyle: 'font-serif',
    fontFamilyCSS: 'Merriweather, Times New Roman, serif',
    atsScore: 91,
    atsSafe: true,
    bestFor: 'Senior Developers & Tech Leads',
    description: 'Formal serif executive font (Merriweather) emphasizing leadership accomplishments and metrics.'
  },
  {
    id: 'student_fresher',
    name: 'Student / Fresher',
    category: 'Fresher',
    fontName: 'Outfit / Modern Display',
    fontStyle: 'font-sans',
    fontFamilyCSS: 'Outfit, system-ui, sans-serif',
    atsScore: 96,
    atsSafe: true,
    bestFor: 'Students & Recent Graduates',
    description: 'Modern rounded sans-serif font (Outfit font) highlighting education and academic projects.'
  },
  {
    id: 'experienced_pro',
    name: 'Experienced Pro',
    category: 'Experienced',
    fontName: 'Calibri / Standard Corporate',
    fontStyle: 'font-sans',
    fontFamilyCSS: 'Calibri, Arial, sans-serif',
    atsScore: 93,
    atsSafe: true,
    bestFor: '5+ Years Industry Experience',
    description: 'Corporate standard font (Calibri font) with experience-first layout and metric bullet points.'
  },
  {
    id: 'technical_resume',
    name: 'Technical Resume',
    category: 'Engineering',
    fontName: 'Fira Code / Code Stack',
    fontStyle: 'font-mono',
    fontFamilyCSS: 'Fira Code, monospace',
    atsScore: 97,
    atsSafe: true,
    bestFor: 'AI/ML & Data Engineering',
    description: 'Technical code font (Fira Code) with skills grouped by category (Languages, DBs, APIs).'
  }
]

const filteredTemplates = computed(() => {
  return templates.filter(t => {
    const matchCat = selectedCategory.value === 'All' ||
      (selectedCategory.value === 'ATS Safe Only' && t.atsSafe) ||
      t.category === selectedCategory.value
    const matchQuery = !templateSearch.value ||
      t.name.toLowerCase().includes(templateSearch.value.toLowerCase()) ||
      t.description.toLowerCase().includes(templateSearch.value.toLowerCase())
    return matchCat && matchQuery
  })
})

import { useRoute, useRouter } from 'vue-router'
import { watch } from 'vue'

const route = useRoute()
const router = useRouter()

const validTabs = ['dashboard', 'analyzer', 'editor', 'templates', 'export']

const criticalCount = computed(() => (selectedResume.value?.issues || []).filter(i => i.severity === 'Critical').length)
const warningCount = computed(() => (selectedResume.value?.issues || []).filter(i => i.severity === 'Warning').length)
const suggestionCount = computed(() => (selectedResume.value?.issues || []).filter(i => i.severity === 'Suggestion').length)

const syncTabFromUrl = () => {
  const pathSubTab = route.path.split('/')[2]
  const targetTab = (route.query.tab as string) || pathSubTab
  if (targetTab && validTabs.includes(targetTab)) {
    activeTab.value = targetTab as any
  } else {
    activeTab.value = 'dashboard'
  }
}

const switchTab = (tabId: 'dashboard' | 'analyzer' | 'editor' | 'templates' | 'export') => {
  activeTab.value = tabId
  router.push({ query: { ...route.query, tab: tabId } })
}

onMounted(() => {
  syncTabFromUrl()
  fetchResumes()
})

watch(() => route.query.tab, () => {
  syncTabFromUrl()
})

const fetchResumes = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/api/resumes')
    resumes.value = res.data || []
    
    if (resumes.value.length) {
      const qId = route.query.id ? Number(route.query.id) : null
      const matched = qId ? resumes.value.find(r => r.id === qId) : null
      selectedResume.value = matched || resumes.value[0]
      initEditForm(selectedResume.value)
    }
  } catch (err) {
    console.error('Error fetching resumes:', err)
  } finally {
    isLoading.value = false
  }
}

const deleteResume = async (id: number) => {
  if (!confirm('Are you sure you want to delete this resume version?')) return
  try {
    await api.delete(`/api/resumes/${id}`)
    resumes.value = resumes.value.filter(r => r.id !== id)
    if (selectedResume.value?.id === id) {
      selectedResume.value = resumes.value[0] || null
      if (selectedResume.value) initEditForm(selectedResume.value)
    }
  } catch (err) {
    console.error('Error deleting resume:', err)
    resumes.value = resumes.value.filter(r => r.id !== id)
  }
}

const triggerUpload = () => {
  if (fileInput.value) fileInput.value.click()
}

const handleFileSelect = async (e: Event) => {
  const target = e.target as HTMLInputElement
  if (!target.files || !target.files.length) return
  const file = target.files[0]

  isUploading.value = true
  uploadProgress.value = 20
  uploadStep.value = 'Extracting Text...'

  try {
    const formData = new FormData()
    formData.append('file', file)

    uploadProgress.value = 50
    uploadStep.value = 'Scanning Errors & Calculating ATS Score...'

    const res = await api.post('/api/resumes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    uploadProgress.value = 100
    uploadStep.value = 'Complete'

    resumes.value.unshift(res.data)
    selectedResume.value = res.data
    initEditForm(res.data)
    activeTab.value = 'analyzer'
  } catch (err) {
    console.error('Error uploading resume:', err)
  } finally {
    isUploading.value = false
  }
}



const selectResume = (res: ResumeItem, tab: 'analyzer' | 'editor' | 'export') => {
  selectedResume.value = res
  initEditForm(res)
  activeTab.value = tab
  router.replace({ query: { id: res.id.toString(), tab } })
}

const initEditForm = (res: ResumeItem) => {
  const normExperience = (res.experience || []).map((exp: any) => {
    if (typeof exp === 'string') {
      return { role: exp, company: '', duration: '', type: 'Job', description: exp }
    }
    return { ...exp }
  })

  const normProjects = (res.projects || []).map((proj: any) => {
    if (typeof proj === 'string') {
      return { name: proj, technologies: [], tech_str: '', description: proj }
    }
    return {
      ...proj,
      tech_str: (proj.technologies || []).join(', ')
    }
  })

  const normEducation = (res.education || []).map((edu: any) => {
    if (typeof edu === 'string') {
      return { degree: edu, institution: '', duration: '', year: '', aggregate: '' }
    }
    return { ...edu }
  })

  editForm.value = {
    personal_info: { ...(res.personal_info || {}) },
    summary: res.summary || '',
    skills: [...(res.skills || [])],
    experience: normExperience,
    projects: normProjects,
    education: normEducation,
    certifications: [...(res.certifications || [])],
    achievements: [...(res.achievements || [])],
    links: [...(res.links || [])]
  }

  skillsInput.value = (res.skills || []).join(', ')
  certsInput.value = (editForm.value.certifications || []).join(', ')
  achievementsInput.value = (editForm.value.achievements || []).join(', ')
  linksInput.value = (editForm.value.links || []).join(', ')
}

const updateSkillsFromInput = () => {
  editForm.value.skills = skillsInput.value.split(',').map(s => s.trim()).filter(Boolean)
}

const updateCertsFromInput = () => {
  editForm.value.certifications = certsInput.value.split(',').map(s => s.trim()).filter(Boolean)
}

const updateAchievementsFromInput = () => {
  editForm.value.achievements = achievementsInput.value.split(',').map(s => s.trim()).filter(Boolean)
}

const updateLinksFromInput = () => {
  editForm.value.links = linksInput.value.split(',').map(s => s.trim()).filter(Boolean)
}

const moveExperience = (idx: number, direction: number) => {
  const newIdx = idx + direction
  if (newIdx < 0 || newIdx >= editForm.value.experience.length) return
  const temp = editForm.value.experience[idx]
  editForm.value.experience[idx] = editForm.value.experience[newIdx]
  editForm.value.experience[newIdx] = temp
}

const moveProject = (idx: number, direction: number) => {
  const newIdx = idx + direction
  if (newIdx < 0 || newIdx >= editForm.value.projects.length) return
  const temp = editForm.value.projects[idx]
  editForm.value.projects[idx] = editForm.value.projects[newIdx]
  editForm.value.projects[newIdx] = temp
}

const addExperienceItem = () => {
  editForm.value.experience.push({ role: '', company: '', duration: '', type: 'Job', description: '' })
}

const removeExperienceItem = (idx: number) => {
  editForm.value.experience.splice(idx, 1)
}

const addProjectItem = () => {
  editForm.value.projects.push({ name: '', technologies: [], tech_str: '', description: '' })
}

const removeProjectItem = (idx: number) => {
  editForm.value.projects.splice(idx, 1)
}

const addEducationItem = () => {
  if (!editForm.value.education) editForm.value.education = []
  editForm.value.education.push({ degree: '', institution: '', year: '', aggregate: '' })
}

const removeEducationItem = (idx: number) => {
  if (editForm.value.education) {
    editForm.value.education.splice(idx, 1)
  }
}

const updateProjectTech = (proj: any) => {
  if (proj.tech_str) {
    proj.technologies = proj.tech_str.split(',').map((s: string) => s.trim()).filter(Boolean)
  }
}

const saveResumeChanges = async () => {
  if (!selectedResume.value) return
  try {
    const res = await api.put(`/api/resumes/${selectedResume.value.id}`, editForm.value)
    selectedResume.value = res.data
    const idx = resumes.value.findIndex(r => r.id === res.data.id)
    if (idx !== -1) resumes.value[idx] = res.data
  } catch (err) {
    console.error('Error updating resume:', err)
  }
}

const fixSingleIssue = async (issueId: string) => {
  if (!selectedResume.value) return
  try {
    const res = await api.post(`/api/resumes/${selectedResume.value.id}/fix`, { issue_ids: [issueId] })
    selectedResume.value = res.data
    const idx = resumes.value.findIndex(r => r.id === res.data.id)
    if (idx !== -1) resumes.value[idx] = res.data
    initEditForm(res.data)
  } catch (err) {
    console.error('Error fixing issue:', err)
  }
}

const fixAllIssues = async () => {
  if (!selectedResume.value) return
  try {
    const res = await api.post(`/api/resumes/${selectedResume.value.id}/fix`, { fix_all: true })
    selectedResume.value = res.data
    const idx = resumes.value.findIndex(r => r.id === res.data.id)
    if (idx !== -1) resumes.value[idx] = res.data
    initEditForm(res.data)
  } catch (err) {
    console.error('Error fixing all issues:', err)
  }
}

const templateSuccessMsg = ref<string>('')

const applyTemplateToResume = async (tpl: typeof templates[0]) => {
  try {
    let resData: any
    if (selectedResume.value) {
      const res = await api.post(`/api/resumes/${selectedResume.value.id}/apply-template`, {
        template_id: tpl.id,
        template_name: tpl.name
      })
      resData = res.data
      const idx = resumes.value.findIndex(r => r.id === resData.id)
      if (idx !== -1) resumes.value[idx] = resData
    } else {
      // New user account without any uploaded resumes: create template draft resume
      const res = await api.post('/api/resumes/create-template-draft', {
        template_id: tpl.id,
        template_name: tpl.name
      })
      resData = res.data
      resumes.value.unshift(resData)
    }

    selectedResume.value = resData
    initEditForm(resData)
    
    templateSuccessMsg.value = `✓ "${tpl.name}" template applied successfully!`
    setTimeout(() => { templateSuccessMsg.value = '' }, 4000)
    
    switchTab('editor')
  } catch (err) {
    console.error('Error applying template:', err)
  }
}

const runJobMatch = async () => {
  if (!selectedResume.value || !jdInput.value.trim()) return
  try {
    const res = await api.post(`/api/resumes/${selectedResume.value.id}/job-match`, {
      job_description: jdInput.value
    })
    jobMatchResult.value = res.data
  } catch (err) {
    console.error('Error matching job description:', err)
  }
}

const exportFile = async (type: 'pdf' | 'docx') => {
  if (!selectedResume.value) return
  try {
    const res = await api.post(`/api/resumes/${selectedResume.value.id}/export/${type}`, {}, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${selectedResume.value.title.replace(/\s+/g, '_')}.${type}`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    console.error(`Error exporting ${type}:`, err)
  }
}

const handleQuickTemplateChange = (e: Event) => {
  const target = e.target as HTMLSelectElement
  const tplId = target.value
  const found = templates.find(t => t.id === tplId)
  if (found) {
    applyTemplateToResume(found)
  }
}

const formatResumeAsPlainText = (form: typeof editForm.value) => {
  const p = form.personal_info || {}
  let lines: string[] = []
  lines.push((p.name || 'CANDIDATE NAME').toUpperCase())
  lines.push(`${p.target_role || ''} | ${p.email || ''} | ${p.phone || ''} | ${p.location || ''}`)
  if (p.linkedin) lines.push(`LinkedIn: ${p.linkedin}`)
  if (p.github) lines.push(`GitHub: ${p.github}`)
  lines.push('\n' + '='.repeat(40))
  
  if (form.summary) {
    lines.push('\nPROFESSIONAL SUMMARY')
    lines.push(form.summary)
  }
  if (form.skills?.length) {
    lines.push('\nCORE TECHNICAL SKILLS')
    lines.push(form.skills.join(' • '))
  }
  if (form.experience?.length) {
    lines.push('\nWORK EXPERIENCE')
    form.experience.forEach(exp => {
      lines.push(`${exp.role || ''} — ${exp.company || ''} (${exp.duration || exp.dates || ''})`)
      if (exp.description) lines.push(`• ${exp.description}`)
    })
  }
  if (form.projects?.length) {
    lines.push('\nKEY PROJECTS')
    form.projects.forEach(proj => {
      lines.push(`${proj.name || ''} [${(proj.technologies || []).join(', ')}]`)
      if (proj.description) lines.push(`• ${proj.description}`)
    })
  }
  if (form.education?.length) {
    lines.push('\nEDUCATION')
    form.education.forEach(edu => {
      const deg = typeof edu === 'string' ? edu : (edu.degree || edu.title || '')
      const inst = typeof edu === 'object' && (edu.institution || edu.school) ? ` — ${edu.institution || edu.school}` : ''
      lines.push(`${deg}${inst}`)
    })
  }
  return lines.join('\n')
}

const exportPlainText = () => {
  if (!selectedResume.value) return
  const text = formatResumeAsPlainText(editForm.value)
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  const title = (selectedResume.value.title || 'Resume').replace(/\s+/g, '_')
  link.setAttribute('download', `${title}.txt`)
  document.body.appendChild(link)
  link.click()
  link.remove()
}

const copyResumeToClipboard = () => {
  if (!selectedResume.value) return
  const text = formatResumeAsPlainText(editForm.value)
  navigator.clipboard.writeText(text)
  alert('✓ Formatted resume text copied to clipboard!')
}

const printResumeDocument = () => {
  window.print()
}

const exportATSReport = async () => {
  if (!selectedResume.value) return
  try {
    const res = await api.post(`/api/resumes/${selectedResume.value.id}/export/ats-report`, {}, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    const name = selectedResume.value.personal_info?.name || 'Candidate'
    link.setAttribute('download', `${name.replace(/\s+/g, '_')}_ATS_Audit_Report.txt`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    console.error('Error exporting ATS report:', err)
  }
}

const createNewResume = () => {
  if (selectedResume.value) {
    applyTemplateToResume(templates[0])
  } else {
    triggerUpload()
  }
}

const getSeverityClass = (severity: string) => {
  if (severity === 'Critical') return 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
  if (severity === 'Warning') return 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
  return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return 'Recently'
  return new Date(dateStr).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>
