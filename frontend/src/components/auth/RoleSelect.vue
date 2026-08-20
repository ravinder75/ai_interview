<template>
  <div class="space-y-1">
    <label class="font-semibold text-slate-300 text-xs block">Target Role</label>
    <div class="space-y-2">
      <select
        :value="isCustom ? 'Other' : modelValue"
        @change="handleSelectChange"
        class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-slate-100 text-xs outline-none focus:border-indigo-500 transition"
      >
        <option value="" disabled>Select your target role</option>
        <option v-for="role in roles" :key="role" :value="role">{{ role }}</option>
      </select>

      <input
        v-if="isCustom"
        v-model="customRole"
        @input="$emit('update:modelValue', customRole)"
        type="text"
        placeholder="Enter custom target role"
        class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-slate-100 text-xs placeholder-slate-500 outline-none focus:border-indigo-500 transition"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits(['update:modelValue'])

const roles = [
  // IT, Infrastructure & Systems Engineering
  'Software Engineer',
  'Frontend Developer',
  'Backend Developer',
  'Full Stack Developer',
  'Python Developer',
  'Java Developer',
  'JavaScript Developer',
  'React Developer',
  'Vue Developer',
  'Node.js Developer',
  'Mobile Developer',
  'Android Developer',
  'iOS Developer',
  'Device Management Specialist',
  'Mobile Device Management (MDM) Administrator',
  'System Administrator / Systems Engineer',
  'IT Support & Infrastructure Specialist',
  'Network Engineer',
  'Data Analyst',
  'Data Scientist',
  'Machine Learning Engineer',
  'AI Engineer',
  'DevOps Engineer',
  'Cloud Engineer',
  'Cybersecurity Engineer',
  'QA Engineer',
  'Automation Tester',
  'Database Developer',
  'SQL Developer',
  'Product Manager',
  'Project Manager',
  'Business Analyst',
  'UI/UX Designer',
  
  // Medical, Healthcare & Medical Coding Branches
  'Medical Coding Specialist',
  'Certified Professional Coder (CPC)',
  'Medical Billing & Coding Specialist',
  'Inpatient / Outpatient Coder',
  'Clinical Documentation Specialist (CDIS)',
  'Health Information Management (HIM) Specialist',
  'Medical Officer / Doctor',
  'General Physician',
  'Staff Nurse / Nursing Officer',
  'Pharmacist',
  'Medical Lab Technician',
  'Hospital Administrator',
  'Radiology Technician',
  
  // Core Engineering & Technical Branches
  'Mechanical Engineer',
  'Electrical & Electronics Engineer',
  'Civil Engineer',
  'Chemical Engineer',
  'Biomedical Engineer',
  'Automobile Engineer',
  'Aeronautical Engineer',
  
  // Business, Operations, Finance & Management
  'Operations Manager / Specialist',
  'Customer Support Specialist',
  'Client Success Manager',
  'Financial Analyst',
  'Chartered Accountant (CA)',
  'HR Manager / Specialist',
  'Marketing Executive / Manager',
  'Sales Operations Specialist',
  'Supply Chain & Logistics Manager',
  'Legal Advisor / Corporate Lawyer',

  'Other'
]

const isCustom = ref(false)
const customRole = ref('')

watch(() => props.modelValue, (val) => {
  if (val && !roles.includes(val)) {
    isCustom.value = true
    customRole.value = val
  }
}, { immediate: true })

const handleSelectChange = (e: Event) => {
  const val = (e.target as HTMLSelectElement).value
  if (val === 'Other') {
    isCustom.value = true
    emit('update:modelValue', customRole.value)
  } else {
    isCustom.value = false
    emit('update:modelValue', val)
  }
}
</script>
