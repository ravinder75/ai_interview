<template>
  <div class="max-w-6xl mx-auto space-y-6 py-6 font-sans">

    <!-- Loading State Screen -->
    <div v-if="loading" class="glass-card rounded-2xl p-12 border border-slate-800 text-center space-y-4 my-8 bg-slate-950">
      <div class="w-16 h-16 rounded-full bg-indigo-600/20 text-indigo-400 mx-auto flex items-center justify-center animate-pulse border border-indigo-500/30">
        <Loader2 class="w-8 h-8 animate-spin" />
      </div>
      <h2 class="text-xl font-extrabold text-slate-100">Executing Evidence-Based Assessment Engine...</h2>
      <p class="text-xs text-slate-400 font-mono">Running answer-level evaluations, computing deterministic metric aggregations, verifying project claims, and assembling report for session {{ sessionId }}...</p>
    </div>

    <!-- Main Evidence-Based Assessment Report Card -->
    <div v-else-if="report" class="glass-card rounded-2xl p-8 border border-slate-800 space-y-8 animate-fadeIn bg-slate-950">
      
      <!-- Zero Answer Notice Banner -->
      <div v-if="report.report_type === 'NO_RESPONSE' || report.questions_answered === 0" class="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start gap-3 shadow-md">
        <AlertCircle class="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div class="space-y-1">
          <strong class="font-bold text-amber-200 block text-sm">⚠️ Interview Exited Without Answers</strong>
          <p class="leading-relaxed text-amber-300/90">
            No performance score was generated because no interview answers were submitted. Start a new interview to receive a meaningful performance assessment.
          </p>
        </div>
      </div>

      <!-- Top Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div class="flex items-center flex-wrap gap-2">
            <span class="text-[10px] text-indigo-400 font-extrabold uppercase tracking-widest font-mono bg-indigo-500/10 px-2.5 py-0.5 rounded border border-indigo-500/20">EVIDENCE-BASED AI ASSESSMENT</span>
            
            <!-- Trust Label Badge -->
            <span :class="[
              'text-[10px] font-extrabold uppercase tracking-wider font-mono px-2.5 py-0.5 rounded border',
              trustBadgeClass
            ]">
              🛡️ TRUST LEVEL: {{ report.trust_label || 'No Evidence' }}
            </span>

            <span class="text-[10px] text-slate-400 font-mono">Completion: {{ report.completion_percentage || 0 }}%</span>
            <span class="text-[10px] text-slate-400 font-mono">Answered: {{ report.questions_answered || 0 }}/{{ report.questions_presented || 5 }}</span>
            <span class="text-[10px] text-slate-500 font-mono">Session ID: {{ sessionId }}</span>
          </div>

          <h1 class="text-2xl font-extrabold text-slate-100 mt-2 flex items-center gap-2">
            🎯 {{ (report.report_type === 'NO_RESPONSE' || report.questions_answered === 0) ? 'AI MOCK INTERVIEW SESSION REPORT' : 'AI MOCK INTERVIEW PERFORMANCE & SKILL REPORT' }}
          </h1>
          <div class="flex flex-wrap items-center gap-3 text-xs text-slate-400 mt-1">
            <span>Candidate: <strong class="text-slate-200">{{ report.candidate?.name || 'Candidate' }}</strong></span>
            <span>Target Role: <strong class="text-indigo-300 font-mono">{{ report.candidate?.target_role || 'Software Engineer' }}</strong></span>
            <span v-if="report.created_at || report.completed_at">Date: <strong class="text-slate-300 font-mono">{{ formatDate(report.created_at || report.completed_at) }}</strong></span>
            <span v-if="report.recommendation || report.final_recommendation">Status: 
              <strong :class="report.overall_score >= 75 ? 'text-emerald-400 font-bold' : (report.overall_score !== null ? 'text-amber-400 font-bold' : 'text-slate-400 font-bold')">
                {{ report.recommendation || (report.questions_answered === 0 ? 'Not Assessed' : 'Evaluated') }}
              </strong>
            </span>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <button
            @click="fetchReport(true)"
            :disabled="loading || report.questions_answered === 0"
            :title="report.questions_answered === 0 ? 'Nothing to evaluate — no candidate answers submitted.' : 'Re-evaluate report'"
            :class="['btn-secondary py-2.5 px-4 text-xs font-bold flex items-center gap-1.5', report.questions_answered === 0 ? 'opacity-50 cursor-not-allowed' : '']"
          >
            <RefreshCw :class="['w-4 h-4 text-indigo-400', loading ? 'animate-spin' : '']" />
            <span>Re-Evaluate Engine</span>
          </button>
          <router-link to="/mock-interview" class="btn-primary py-2.5 px-5 text-xs font-bold shadow-lg shadow-indigo-600/30">
            [ Start New Interview ]
          </router-link>
        </div>
      </div>

      <!-- Overall Deterministic Scores Grid -->
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <BarChart3 class="w-4 h-4 text-indigo-400" />
            <span>DETERMINISTIC CATEGORY PERFORMANCE SCORES</span>
          </h3>
          <span class="text-[11px] text-slate-500 font-mono">Calculated via backend math engine</span>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
          <div class="bg-indigo-950/40 p-4 rounded-xl border border-indigo-500/40 text-center space-y-1 shadow-lg cursor-pointer hover:border-indigo-400 transition-all" @click="openEvidenceModal('Overall Score', report.overall_score, 'Primary weighted performance average across assessed dimensions.')">
            <span class="text-[10px] text-indigo-300 font-bold uppercase tracking-wider block">OVERALL</span>
            <span class="text-2xl font-extrabold text-indigo-400 font-mono">
              {{ getDisplayScore(report.overall_score) }}
            </span>
            <span class="text-[9px] text-indigo-400/80 block font-mono">Click for evidence</span>
          </div>

          <div v-for="(catName, catKey) in categoryLabels" :key="catKey" 
               class="bg-slate-900/90 p-4 rounded-xl border border-slate-800 text-center space-y-1 hover:border-slate-700 transition-all cursor-pointer"
               @click="openEvidenceModal(catName, getCategoryScore(catKey), getCategoryDescription(catKey))">
            <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">{{ catName }}</span>
            <span :class="[
              'text-xl font-bold font-mono',
              getCategoryScore(catKey) !== null ? 'text-slate-100' : 'text-slate-500 italic text-xs'
            ]">
              {{ getCategoryScore(catKey) !== null ? `${getCategoryScore(catKey)}%` : 'Not assessed' }}
            </span>
            <span class="text-[9px] text-slate-500 block font-mono">{{ getCategoryScore(catKey) !== null ? 'View evidence' : 'Not tested' }}</span>
          </div>
        </div>
      </div>

      <!-- Executive Summary Box -->
      <div v-if="report.summary || report.interview_summary?.summary" class="p-5 rounded-2xl bg-indigo-950/30 border border-indigo-500/30 space-y-2 text-xs">
        <h3 class="font-bold text-indigo-300 uppercase tracking-wider flex items-center gap-2 font-mono">
          <Bot class="w-4 h-4 text-indigo-400" />
          <span>VERIFIED EXECUTIVE ASSESSMENT SUMMARY</span>
        </h3>
        <p class="text-slate-300 leading-relaxed font-sans">
          {{ report.summary || report.interview_summary?.summary }}
        </p>
      </div>

      <!-- Skill Evidence Matrix Table -->
      <div v-if="report.skill_evidence_matrix && report.skill_evidence_matrix.length" class="space-y-3">
        <h3 class="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center justify-between">
          <span class="flex items-center gap-2">
            <Boxes class="w-4 h-4 text-emerald-400" />
            <span>SKILL EVIDENCE MATRIX</span>
          </span>
          <span class="text-[11px] text-slate-400 font-mono">Minimum Evidence Rule Enforced</span>
        </h3>

        <div class="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-950 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th class="p-3">Tested Topic / Skill</th>
                <th class="p-3 text-center">Questions Tested</th>
                <th class="p-3 text-center">Average Score</th>
                <th class="p-3 text-center">Strong / Weak Answers</th>
                <th class="p-3">Evidence Confidence</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60 text-slate-300">
              <tr v-for="(item, idx) in report.skill_evidence_matrix" :key="idx" class="hover:bg-slate-900/80 transition-colors">
                <td class="p-3 font-bold text-slate-200 font-mono">{{ item.skill }}</td>
                <td class="p-3 text-center font-mono font-semibold">{{ item.questions_tested }}</td>
                <td class="p-3 text-center font-mono">
                  <span v-if="item.average_score !== null" :class="item.average_score >= 75 ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold'">
                    {{ item.average_score }}/100
                  </span>
                  <span v-else class="text-slate-500 italic text-[11px]">N/A</span>
                </td>
                <td class="p-3 text-center font-mono">
                  <span class="text-emerald-400 font-bold">{{ item.strong_answers }}</span> / 
                  <span class="text-amber-400 font-bold">{{ item.weak_answers }}</span>
                </td>
                <td class="p-3 font-mono text-[11px]">
                  <span :class="item.questions_tested <= 1 ? 'text-amber-400 font-bold' : 'text-indigo-300 font-semibold'">
                    {{ item.evidence_confidence }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Speaking Analysis Card (Voice Mode Only / Handled Cleanly) -->
      <div v-if="report.speaking_metrics && typeof report.speaking_metrics === 'object'" class="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
        <h3 class="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center justify-between">
          <span class="flex items-center gap-2">
            <Mic class="w-4 h-4 text-purple-400" />
            <span>DETERMINISTIC SPEAKING METRICS & PATTERNS</span>
          </span>
          <span class="text-[11px] font-mono text-purple-300 bg-purple-950/40 px-2 py-0.5 rounded border border-purple-500/30">Voice Mode Session</span>
        </h3>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
          <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
            <span class="text-slate-400 text-[10px] block uppercase">Pacing (WPM)</span>
            <span class="text-lg font-bold text-purple-300">{{ report.speaking_metrics.words_per_minute }} WPM</span>
            <span class="text-[10px] text-slate-500 block mt-0.5">{{ report.speaking_metrics.speech_indicators?.pacing }}</span>
          </div>

          <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
            <span class="text-slate-400 text-[10px] block uppercase">Response Latency</span>
            <span class="text-lg font-bold text-indigo-300">{{ report.speaking_metrics.average_response_latency_seconds }}s</span>
            <span class="text-[10px] text-slate-500 block mt-0.5">Average delay before response</span>
          </div>

          <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
            <span class="text-slate-400 text-[10px] block uppercase">Filler Rate</span>
            <span class="text-lg font-bold text-emerald-400">{{ report.speaking_metrics.filler_rate_percent }}%</span>
            <span class="text-[10px] text-slate-500 block mt-0.5">{{ report.speaking_metrics.filler_word_count }} filler words detected</span>
          </div>

          <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
            <span class="text-slate-400 text-[10px] block uppercase">Total Spoken Words</span>
            <span class="text-lg font-bold text-slate-200">{{ report.speaking_metrics.total_words }} words</span>
            <span class="text-[10px] text-slate-500 block mt-0.5">Duration: {{ report.speaking_metrics.speaking_duration_seconds }}s</span>
          </div>
        </div>
      </div>

      <div v-else-if="report.speaking_metrics === 'Not assessed — text mode interview' || !report.speaking_metrics" class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-400 flex items-center justify-between font-mono">
        <span class="flex items-center gap-2">
          <MicOff class="w-4 h-4 text-slate-500" />
          <span>Speaking Analysis: Not assessed — text interview mode.</span>
        </span>
        <span class="text-[11px] text-slate-500">Excluded from communication latency metrics</span>
      </div>

      <!-- Project & Technology Claim Verification Grid -->
      <div v-if="report.claim_verification" class="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3 text-xs">
        <h3 class="font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2 font-mono">
          <FileCheck class="w-4 h-4 text-blue-400" />
          <span>PROJECT & TECHNOLOGY CLAIM VERIFICATION GRAPH</span>
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Verified Technologies -->
          <div class="p-4 rounded-xl bg-slate-950 border border-emerald-500/20 space-y-2">
            <h4 class="font-bold text-emerald-400 uppercase text-[11px] flex items-center gap-1.5 font-mono">
              <CheckCircle class="w-3.5 h-3.5" />
              <span>Verified Technologies & Concepts ({{ report.claim_verification.verified_technologies?.length || 0 }})</span>
            </h4>
            <ul v-if="report.claim_verification.verified_technologies?.length" class="space-y-1.5 font-mono text-[11px]">
              <li v-for="(v, idx) in report.claim_verification.verified_technologies" :key="idx" class="flex items-start gap-2 text-slate-300">
                <span class="text-emerald-400 font-bold">✓</span>
                <div>
                  <strong class="text-slate-100">{{ v.technology }}</strong>
                  <p class="text-slate-400 text-[10px] font-sans">{{ v.evidence }}</p>
                </div>
              </li>
            </ul>
            <p v-else class="text-slate-500 italic text-[11px]">No technologies verified yet.</p>
          </div>

          <!-- Unverified Claims -->
          <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <h4 class="font-bold text-amber-400 uppercase text-[11px] flex items-center gap-1.5 font-mono">
              <AlertCircle class="w-3.5 h-3.5" />
              <span>Not Assessed / Listed Only ({{ report.claim_verification.unverified_claims?.length || 0 }})</span>
            </h4>
            <ul v-if="report.claim_verification.unverified_claims?.length" class="space-y-1.5 font-mono text-[11px]">
              <li v-for="(u, idx) in report.claim_verification.unverified_claims" :key="idx" class="flex items-start gap-2 text-slate-300">
                <span class="text-amber-400 font-bold">ℹ</span>
                <div>
                  <strong class="text-slate-200">{{ u.technology }}</strong>
                  <p class="text-slate-400 text-[10px] font-sans">{{ u.evidence }}</p>
                </div>
              </li>
            </ul>
            <p v-else class="text-slate-500 italic text-[11px]">All profile skills were assessed.</p>
          </div>
        </div>
      </div>

      <!-- Question-by-Question Review -->
      <div v-if="questionList.length" class="space-y-4 pt-4 border-t border-slate-800">
        <h3 class="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center justify-between font-mono">
          <span>📜 INDEPENDENT QUESTION-BY-QUESTION REVIEW</span>
          <span class="text-slate-500 font-normal">{{ questionList.length }} Questions Analyzed</span>
        </h3>

        <div class="space-y-4">
          <div v-for="(q, idx) in questionList" :key="idx" class="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3 text-xs">
            <div class="flex items-center justify-between border-b border-slate-800 pb-2">
              <div class="flex items-center gap-2">
                <span class="font-bold text-indigo-400 uppercase tracking-wider font-mono">Q{{ Number(idx) + 1 }} • {{ q.category || 'Technical' }}</span>
                <span v-if="q.difficulty" class="text-[10px] text-slate-400 font-mono px-2 py-0.5 bg-slate-950 rounded border border-slate-800">Diff: {{ q.difficulty }}</span>
              </div>

              <span v-if="q.score !== null && q.score !== undefined" 
                    :class="[
                      'px-2.5 py-0.5 rounded font-mono font-bold border',
                      q.score >= 75 ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : (q.score >= 60 ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20')
                    ]">
                Score: {{ q.score }}/100
              </span>
            </div>

            <div class="space-y-1">
              <span class="text-[11px] font-bold text-slate-400 block font-mono">ACTUAL QUESTION ASKED:</span>
              <p class="text-slate-100 font-medium bg-slate-950 p-3 rounded-xl border border-slate-800/60">{{ q.question }}</p>
            </div>

            <div class="space-y-1">
              <span class="text-[11px] font-bold text-slate-400 block font-mono">CANDIDATE ANSWER / TRANSCRIPT EVIDENCE:</span>
              <p class="text-slate-300 bg-slate-950 p-3 rounded-xl border border-slate-800/60 font-sans leading-relaxed">{{ q.candidate_answer || q.answer || 'Not answered' }}</p>
            </div>

            <!-- Factual Corrections Alert -->
            <div v-if="q.factual_corrections && q.factual_corrections.length" class="p-3 rounded-xl bg-red-950/20 border border-red-500/30 text-red-300 space-y-1 text-[11px]">
              <span class="font-bold uppercase block text-red-400 font-mono">⚠️ FACTUAL CORRECTIONS IDENTIFIED:</span>
              <ul class="space-y-1">
                <li v-for="(fc, fidx) in q.factual_corrections" :key="fidx">
                  Candidate said: <em>"{{ fc.incorrect_claim }}"</em> → Correct: <strong>{{ fc.correct_information }}</strong>
                </li>
              </ul>
            </div>

            <div v-if="q.strengths?.length || q.weaknesses?.length || q.evidence?.length" class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              <div v-if="q.strengths?.length" class="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/20 text-emerald-300 space-y-1">
                <span class="font-bold text-[11px] uppercase block font-mono">Verified Strengths:</span>
                <ul class="list-disc list-inside space-y-1 text-[11px]">
                  <li v-for="(s, sidx) in q.strengths" :key="sidx">{{ s }}</li>
                </ul>
              </div>

              <div v-if="q.weaknesses?.length" class="p-3 rounded-xl bg-amber-950/20 border border-amber-500/20 text-amber-300 space-y-1">
                <span class="font-bold text-[11px] uppercase block font-mono">Areas to Improve / Missing Details:</span>
                <ul class="list-disc list-inside space-y-1 text-[11px]">
                  <li v-for="(w, widx) in q.weaknesses" :key="widx">{{ w }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Strengths & Improvements Grid -->
      <div v-if="(report.strengths && report.strengths.length) || (report.weaknesses && report.weaknesses.length)" class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
        <div v-if="report.strengths && report.strengths.length" class="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <h3 class="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2 font-mono">
            <CheckCircle class="w-4 h-4" />
            <span>EVIDENCE-VERIFIED STRENGTHS</span>
          </h3>
          <ul class="space-y-2 text-xs text-slate-300">
            <li v-for="(str, idx) in report.strengths" :key="idx" class="flex items-start gap-2">
              <span class="text-emerald-400 font-bold">✓</span>
              <span>{{ str }}</span>
            </li>
          </ul>
        </div>

        <div v-if="report.weaknesses && report.weaknesses.length" class="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <h3 class="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2 font-mono">
            <AlertCircle class="w-4 h-4" />
            <span>IDENTIFIED GAPS & AREAS FOR PRACTICE</span>
          </h3>
          <ul class="space-y-2 text-xs text-slate-300">
            <li v-for="(imp, idx) in report.weaknesses" :key="idx" class="flex items-start gap-2">
              <span class="text-amber-400 font-bold">💡</span>
              <span>{{ imp }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Personalized Improvement Plan -->
      <div v-if="report.personalized_learning_plan && report.personalized_learning_plan.length" class="p-5 rounded-2xl bg-indigo-950/30 border border-indigo-500/30 space-y-3 text-xs">
        <h3 class="font-bold text-indigo-300 uppercase tracking-wider font-mono flex items-center gap-2">
          <Target class="w-4 h-4 text-indigo-400" />
          <span>🚀 PERSONALIZED PRACTICE & DRILL PLAN</span>
        </h3>
        <div class="space-y-3">
          <div v-for="(item, idx) in report.personalized_learning_plan" :key="idx" class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
            <div class="flex items-center justify-between font-mono font-bold text-indigo-400 text-[11px]">
              <span>Priority #{{ item.priority || (Number(idx) + 1) }}: {{ item.topic || item.area }}</span>
            </div>
            <p v-if="item.action" class="text-emerald-400 font-medium">Recommended Action: {{ item.action }}</p>
            <p v-if="item.practice" class="text-slate-400 italic">Drill: {{ item.practice }}</p>
          </div>
        </div>
      </div>

      <!-- Report Limitations & Session Metadata -->
      <div v-if="report.limitations && report.limitations.length" class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1 text-xs text-slate-400 font-mono">
        <h4 class="font-bold text-slate-300 uppercase text-[10px]">REPORT LIMITATIONS & TRANSPARENCY:</h4>
        <ul class="list-disc list-inside space-y-0.5 text-[11px]">
          <li v-for="(lim, idx) in report.limitations" :key="idx">{{ lim }}</li>
        </ul>
      </div>

    </div>

    <!-- Empty / Failed State Screen -->
    <div v-else class="glass-card rounded-2xl p-12 border border-slate-800 text-center space-y-5 my-8 bg-slate-950">
      <div class="w-16 h-16 rounded-full bg-amber-500/10 text-amber-400 mx-auto flex items-center justify-center border border-amber-500/20">
        <AlertCircle class="w-8 h-8" />
      </div>
      <div class="space-y-1 max-w-md mx-auto">
        <h2 class="text-xl font-extrabold text-slate-100">Evaluation Report Not Available</h2>
        <p class="text-xs text-slate-400 font-mono">No stored evidence report found for Session ID: <strong class="text-slate-200">{{ sessionId }}</strong>.</p>
      </div>
      <div class="flex items-center justify-center gap-3 pt-2">
        <button @click="fetchReport(true)" class="btn-primary py-2.5 px-6 text-xs font-bold shadow-lg shadow-indigo-600/30 flex items-center gap-2">
          <RefreshCw class="w-4 h-4" />
          <span>⚡ Generate Evidence Assessment Report</span>
        </button>
        <router-link to="/mock-interview" class="btn-secondary py-2.5 px-5 text-xs font-bold">
          [ Back to Interviews ]
        </router-link>
      </div>
    </div>

    <!-- VIEW EVIDENCE MODAL -->
    <div v-if="showEvidenceModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4 animate-fadeIn">
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-lg w-full space-y-4 shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 class="font-extrabold text-slate-100 font-mono text-sm flex items-center gap-2">
            <Eye class="w-4 h-4 text-indigo-400" />
            <span>EVIDENCE TRACEABILITY: {{ selectedEvidenceTitle }}</span>
          </h3>
          <button @click="showEvidenceModal = false" class="text-slate-400 hover:text-slate-200 font-mono text-xs">✕ Close</button>
        </div>

        <div class="space-y-3 text-xs">
          <div class="flex items-center justify-between bg-slate-950 p-3 rounded-xl border border-slate-800">
            <span class="text-slate-400 font-mono">Backend Score Value:</span>
            <span class="font-extrabold text-indigo-300 font-mono text-sm">
              {{ selectedEvidenceScore !== null ? `${selectedEvidenceScore}%` : 'Not assessed' }}
            </span>
          </div>

          <div class="space-y-1">
            <span class="font-bold text-slate-300 block font-mono">Calculation & Evidence Context:</span>
            <p class="text-slate-300 bg-slate-950 p-3 rounded-xl border border-slate-800 font-sans leading-relaxed">
              {{ selectedEvidenceText }}
            </p>
          </div>
        </div>

        <div class="pt-2 text-right">
          <button @click="showEvidenceModal = false" class="btn-secondary text-xs py-1.5 px-4">Done</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Bot, Loader2, RefreshCw, CheckCircle, AlertCircle, BarChart3, Boxes, Mic, MicOff, FileCheck, Target, Eye } from 'lucide-vue-next'
import { getInterviewReport, generateInterviewReport, api } from '../services/api'

const route = useRoute()
const sessionId = computed(() => (route.params.sessionId || route.params.interviewId || 'live-session') as string)

const loading = ref(true)
const report = ref<any>(null)

const showEvidenceModal = ref(false)
const selectedEvidenceTitle = ref('')
const selectedEvidenceScore = ref<any>(null)
const selectedEvidenceText = ref('')

const categoryLabels: Record<string, string> = {
  technical: 'Technical',
  problem_solving: 'Problem Solving',
  project_understanding: 'Project Depth',
  role_knowledge: 'Role Knowledge',
  communication: 'Communication',
  coding: 'Coding',
  consistency: 'Consistency'
}

const categoryDescriptions: Record<string, string> = {
  technical: 'Evaluates correctness of technical concepts, algorithms, and frameworks mentioned in answers.',
  problem_solving: 'Evaluates candidate triage methodology, debugging structure, and reasoning logic.',
  project_understanding: 'Evaluates candidate knowledge of project architecture, trade-offs, and implementation metrics.',
  role_knowledge: 'Evaluates relevance of candidate experience against target role requirements.',
  communication: 'Evaluates clarity, structure, conciseness, and technical vocabulary in candidate responses.',
  coding: 'Evaluates syntax, edge cases, complexity, and correctness of submitted code solutions.',
  consistency: 'Evaluates performance variance across consecutive question scores.'
}

const trustBadgeClass = computed(() => {
  const label = report.value?.trust_label || 'Medium Evidence'
  if (label.includes('High')) return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
  if (label.includes('Medium')) return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30'
  return 'bg-amber-500/10 text-amber-400 border-amber-500/30'
})

const questionList = computed(() => {
  if (!report.value) return []
  return report.value.question_evaluations || report.value.question_reviews || []
})

const getDisplayScore = (val: any) => {
  if (val !== null && val !== undefined && !isNaN(Number(val)) && Number(val) >= 0) {
    return `${Math.round(Number(val))}/100`
  }
  return 'N/A'
}

const getCategoryScore = (catKey: string) => {
  if (!report.value) return null
  if (report.value.category_scores && report.value.category_scores[catKey] !== undefined) {
    return report.value.category_scores[catKey]
  }
  const keyMap: Record<string, string> = {
    technical: 'technical_score',
    problem_solving: 'problem_solving_score',
    project_understanding: 'project_understanding_score',
    role_knowledge: 'role_knowledge_score',
    communication: 'communication_score',
    coding: 'coding_score',
    consistency: 'consistency_score'
  }
  const topKey = keyMap[catKey]
  if (topKey && report.value[topKey] !== undefined) {
    return report.value[topKey]
  }
  return null
}

const getCategoryDescription = (catKey: string) => {
  return categoryDescriptions[catKey] || 'Evaluates candidate performance in this specific interview dimension.'
}

const openEvidenceModal = (title: string, score: any, desc: string) => {
  selectedEvidenceTitle.value = title
  selectedEvidenceScore.value = score
  selectedEvidenceText.value = desc
  showEvidenceModal.value = true
}

const formatDate = (isoStr: string) => {
  if (!isoStr) return new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
  return new Date(isoStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const fetchReport = async (forceRegenerate = false) => {
  loading.value = true
  try {
    if (forceRegenerate) {
      // Try mock-interview finish endpoint first (creates session + generates report)
      try {
        const finishRes = await api.post(`/api/mock-interviews/${sessionId.value}/finish`)
        if (finishRes.data && finishRes.data.report && typeof finishRes.data.report === 'object' && finishRes.data.report.overall_score !== undefined) {
          report.value = finishRes.data.report
          return
        }
      } catch (e) {
        console.warn('Mock interview finish notice:', e)
      }
      // Fallback to original report generation
      report.value = await generateInterviewReport(sessionId.value)
    } else {
      try {
        report.value = await getInterviewReport(sessionId.value)
      } catch (e) {
        // Try mock-interviews report endpoint
        try {
          const mockRes = await api.get(`/api/mock-interviews/${sessionId.value}/report`)
          if (mockRes.data && typeof mockRes.data === 'object') {
            report.value = mockRes.data
            return
          }
        } catch (e2) {
          console.warn('Mock interview report GET notice:', e2)
        }
        // Final fallback: generate report
        report.value = await generateInterviewReport(sessionId.value)
      }
    }
  } catch (err) {
    console.error('Failed to fetch interview report:', err)
    report.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchReport()
})
</script>
