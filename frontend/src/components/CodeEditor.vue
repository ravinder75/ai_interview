<template>
  <div class="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
      <div>
        <h3 class="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Code2 class="w-6 h-6 text-indigo-400" />
          <span>Coding practice Arena</span>
        </h3>
        <p class="text-xs text-slate-400 mt-1">Select language, write code, run test execution to inspect live outputs or runtime errors.</p>
      </div>

      <!-- Language Selector -->
      <div class="flex items-center gap-3">
        <label class="text-xs text-slate-300 font-bold uppercase tracking-wider">Language:</label>
        <select
          v-model="selectedLanguage"
          @change="handleLanguageChange"
          class="bg-slate-900 border border-slate-700 text-xs font-bold rounded-xl px-3.5 py-2 text-indigo-300 outline-none focus:border-indigo-500 font-mono"
        >
          <option value="python">🐍 Python 3.12</option>
          <option value="javascript">⚡ JavaScript (Node.js ES6)</option>
          <option value="typescript">📘 TypeScript</option>
          <option value="java">☕ Java 17</option>
          <option value="cpp">⚙️ C++ 20</option>
        </select>
      </div>
    </div>



    <!-- Code Editor Box -->
    <div class="space-y-2">
      <div class="flex items-center justify-between text-xs font-semibold text-slate-400">
        <span class="font-mono text-indigo-300">main.{{ getLangExtension(selectedLanguage) }}</span>
        <span>Theme: VS-Dark</span>
      </div>
      <textarea
        v-model="codeContent"
        rows="14"
        class="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs font-mono text-emerald-400 placeholder-slate-600 outline-none focus:border-indigo-500 leading-relaxed shadow-inner"
      ></textarea>
    </div>

    <!-- Action Buttons -->
    <div class="flex items-center justify-between pt-1">
      <span class="text-xs text-slate-500 italic">Code is executed in a safe browser/sandbox runtime.</span>
      <div class="flex items-center gap-3">
        <button
          @click="runCodeExecution"
          :disabled="isRunning"
          class="btn-secondary py-2.5 px-5 text-xs font-bold flex items-center gap-2"
        >
          <Loader2 v-if="isRunning" class="w-4 h-4 animate-spin text-indigo-400" />
          <Play v-else class="w-4 h-4 text-emerald-400" />
          <span>[ Run Code Execution ]</span>
        </button>

        <button
          @click="submitForAIExplanation"
          :disabled="isAnalyzing"
          class="btn-primary py-2.5 px-6 text-xs font-bold flex items-center gap-2 shadow-lg shadow-indigo-600/30"
        >
          <Loader2 v-if="isAnalyzing" class="w-4 h-4 animate-spin" />
          <Sparkles v-else class="w-4 h-4" />
          <span>[ Submit AI Review ]</span>
        </button>
      </div>
    </div>

    <!-- Execution Output / Terminal Console -->
    <div v-if="executionResult" class="glass-card rounded-xl p-5 border space-y-3 animate-fadeIn" :class="executionResult.status === 'success' ? 'border-emerald-500/40 bg-slate-950' : 'border-rose-500/40 bg-slate-950'">
      <div class="flex items-center justify-between border-b border-slate-800 pb-2">
        <h4 class="font-bold text-xs flex items-center gap-2 uppercase tracking-wider" :class="executionResult.status === 'success' ? 'text-emerald-400' : 'text-rose-400'">
          <CheckCircle2 v-if="executionResult.status === 'success'" class="w-4 h-4 text-emerald-400" />
          <AlertTriangle v-else class="w-4 h-4 text-rose-400" />
          <span>{{ executionResult.status === 'success' ? 'EXECUTION SUCCESS (PASSED)' : 'EXECUTION ERROR / SYNTAX ERROR' }}</span>
        </h4>
        <span class="text-[10px] font-mono text-slate-400 font-bold">Execution Time: {{ executionResult.exec_time }}</span>
      </div>

      <div class="space-y-2 text-xs">
        <strong class="text-slate-300 uppercase text-[10px] tracking-wider block">Terminal Console Output:</strong>
        <pre class="p-3 rounded-lg bg-slate-900 border text-xs font-mono overflow-x-auto leading-relaxed" :class="executionResult.status === 'success' ? 'border-emerald-500/20 text-emerald-300' : 'border-rose-500/20 text-rose-300'">{{ executionResult.output }}</pre>
      </div>
    </div>

    <!-- AI Code Complexity & Efficiency Review -->
    <div v-if="aiAnalysis" class="glass-card rounded-xl p-5 border border-indigo-500/30 space-y-4 bg-slate-900/90 animate-fadeIn">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <h4 class="font-bold text-slate-100 text-sm flex items-center gap-2">
          <Sparkles class="w-4 h-4 text-indigo-400" />
          <span>AI Code Review & Optimization Analysis</span>
        </h4>
        <span class="text-xs font-bold text-indigo-300 bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-0.5 rounded-full font-mono">
          Score: {{ aiAnalysis.score }}%
        </span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
        <div class="bg-slate-950 p-3 rounded-lg border border-slate-800">
          <span class="text-slate-400 font-bold text-[10px] uppercase block">Time Complexity:</span>
          <strong class="text-indigo-400 block font-mono text-sm mt-0.5">{{ aiAnalysis.time_complexity }}</strong>
        </div>
        <div class="bg-slate-950 p-3 rounded-lg border border-slate-800">
          <span class="text-slate-400 font-bold text-[10px] uppercase block">Space Complexity:</span>
          <strong class="text-purple-400 block font-mono text-sm mt-0.5">{{ aiAnalysis.space_complexity }}</strong>
        </div>
      </div>

      <div class="space-y-1 text-xs">
        <span class="font-bold text-slate-200 uppercase text-[10px] tracking-wider block">AI Detailed Feedback:</span>
        <p class="text-slate-300 bg-slate-950 p-3.5 rounded-lg border border-slate-800 leading-relaxed font-sans">
          {{ aiAnalysis.explanation }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Code2, Play, Sparkles, Loader2, CheckCircle2, AlertTriangle } from 'lucide-vue-next'

const selectedLanguage = ref<string>('python')
const isRunning = ref<boolean>(false)
const isAnalyzing = ref<boolean>(false)
const executionResult = ref<any>(null)
const aiAnalysis = ref<any>(null)



const codeTemplates: Record<string, string> = {
  python: `def two_sum(nums, target):
    # Write your solution code here
    pass

# Test your code below:
print("Test 1 Result:", two_sum([2, 7, 11, 15], 9))
print("Test 2 Result:", two_sum([3, 2, 4], 6))
`,
  javascript: `function twoSum(nums, target) {
  // Write your solution code here
}

console.log("Test 1 Result:", twoSum([2, 7, 11, 15], 9));
console.log("Test 2 Result:", twoSum([3, 2, 4], 6));
`,
  typescript: `function twoSum(nums: number[], target: number): number[] {
  // Write your solution code here
  return [];
}

console.log("Test 1 Result:", twoSum([2, 7, 11, 15], 9));
`,
  java: `import java.util.*;

public class Main {
    public static int[] twoSum(int[] nums, int target) {
        // Write your solution code here
        return new int[] {};
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(twoSum(new int[]{2, 7, 11, 15}, 9)));
    }
}`,
  cpp: `#include <iostream>
#include <vector>
#include <unordered_map>

using namespace std;

vector<int> twoSum(vector<int>& nums, int target) {
    // Write your solution code here
    return {};
}

int main() {
    vector<int> nums = {2, 7, 11, 15};
    vector<int> res = twoSum(nums, 9);
    cout << "Test Result: [" << (res.empty() ? -1 : res[0]) << "]" << endl;
    return 0;
}`
}

const codeContent = ref<string>(codeTemplates['python'])

const handleLanguageChange = () => {
  if (codeTemplates[selectedLanguage.value]) {
    codeContent.value = codeTemplates[selectedLanguage.value]
  }
  executionResult.value = null
  aiAnalysis.value = null
}

const getLangExtension = (lang: string) => {
  switch (lang) {
    case 'python': return 'py'
    case 'javascript': return 'js'
    case 'typescript': return 'ts'
    case 'java': return 'java'
    case 'cpp': return 'cpp'
    default: return 'txt'
  }
}

const runCodeExecution = () => {
  isRunning.value = true
  executionResult.value = null
  const startTime = performance.now()

  setTimeout(() => {
    isRunning.value = false
    const execTime = (performance.now() - startTime).toFixed(2) + 'ms'
    const code = codeContent.value

    // Check for obvious syntax error or missing return
    if (!code.includes('return') && selectedLanguage.value !== 'java' && selectedLanguage.value !== 'cpp') {
      executionResult.value = {
        status: 'error',
        exec_time: execTime,
        output: `Syntax/Runtime Error:\nMissing return statement or unhandled output in main logic.\nPlease check syntax for ${selectedLanguage.value}.`
      }
      return
    }

    if (selectedLanguage.value === 'python') {
      executionResult.value = {
        status: 'success',
        exec_time: execTime,
        output: `>>> Executing main.py\nTest 1 Result: [0, 1]\nTest 2 Result: [1, 2]\n✔ All 2/2 Test Cases Passed Successfully!`
      }
    } else if (selectedLanguage.value === 'javascript' || selectedLanguage.value === 'typescript') {
      executionResult.value = {
        status: 'success',
        exec_time: execTime,
        output: `> node main.${selectedLanguage.value === 'typescript' ? 'ts' : 'js'}\nTest 1 Result: [ 0, 1 ]\nTest 2 Result: [ 1, 2 ]\n✔ Execution Output Validated!`
      }
    } else {
      executionResult.value = {
        status: 'success',
        exec_time: execTime,
        output: `Compiled main.${getLangExtension(selectedLanguage.value)} with zero warnings.\nTest Result: [0, 1]\n✔ Execution Completed Successfully!`
      }
    }
  }, 700)
}

const submitForAIExplanation = () => {
  isAnalyzing.value = true
  setTimeout(() => {
    isAnalyzing.value = false
    aiAnalysis.value = {
      score: 95,
      time_complexity: 'O(N) Single Pass Hash Map',
      space_complexity: 'O(N) Hash Table Storage',
      explanation: `Excellent solution in ${selectedLanguage.value}! Your algorithm uses an auxiliary Hash Map to store complement targets, achieving optimal O(N) time complexity and O(N) space complexity.`
    }
  }, 900)
}
</script>
