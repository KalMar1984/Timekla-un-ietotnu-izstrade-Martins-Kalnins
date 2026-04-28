<script setup>
import { ref, onMounted, watch, toRaw } from 'vue'
import axios from 'axios'
import { Save, ChevronLeft, Heart, Cloud, Sun } from 'lucide-vue-next'
import { addEntry, getEntryByDate } from '../db'

const props = defineProps({
  initialDate: {
    type: String,
    default: () => new Date().toISOString().split('T')[0]
  }
})

const emit = defineEmits(['saved'])

const date = ref(props.initialDate)
const positiveThings = ref(['', '', ''])
const negativeThings = ref([''])
const gratitude = ref([''])
const emotions = ref([])
const notes = ref('')
const diaryEntry = ref('')
const loading = ref(false)
const message = ref('')

const defaultEmotions = [
  'priecīgs', 'noskumis', 'laimīgs', 'nelaimīgs', 'bēdīgs', 
  'spēka pilns', 'noguris', 'noraizējies', 'dusmīgs', 
  'bailīgs', 'satraukts', 'atpūties', 'jautrs' 
]

const loadEntryData = async (targetDate) => {
  const existing = await getEntryByDate(targetDate)
  if (existing) {
    positiveThings.value = existing.positive_things.length ? existing.positive_things : ['', '', '']
    negativeThings.value = existing.negative_things.length ? existing.negative_things : ['']
    gratitude.value = existing.gratitude.length ? existing.gratitude : ['']
    emotions.value = existing.emotions || []
    notes.value = existing.notes || ''
    diaryEntry.value = existing.diary_entry || ''
  } else {
    // Reset to defaults for a new date
    positiveThings.value = ['', '', '']
    negativeThings.value = ['']
    gratitude.value = ['']
    emotions.value = []
    notes.value = ''
    diaryEntry.value = ''
  }
}

onMounted(() => loadEntryData(date.value))

// Reload if user manually changes date in the form
watch(date, (newDate) => loadEntryData(newDate))

const toggleEmotion = (emotion) => {
  const index = emotions.value.indexOf(emotion)
  if (index === -1) emotions.value.push(emotion)
  else emotions.value.splice(index, 1)
}

const addField = (list) => {
  if (list.length < 3) list.push('')
}

const saveEntry = async () => {
  loading.value = true
  const data = {
    date: date.value,
    positive_things: positiveThings.value.filter(t => t.trim()),
    negative_things: negativeThings.value.filter(t => t.trim()),
    gratitude: gratitude.value.filter(t => t.trim()),
    emotions: emotions.value,
    notes: notes.value,
    diary_entry: diaryEntry.value
  }

  try {
    // 1. Save to local DB first (Offline-first)
    // Deep clone to strip all Vue reactivity proxies which cause DataCloneError
    const cleanData = JSON.parse(JSON.stringify(data))
    await addEntry(cleanData)
    console.log('EntryForm: Saved to Dexie successfully')
    
    // 2. Try to sync with backend
    try {
      const token = localStorage.getItem('token')
      if (token) {
        await axios.post('http://127.0.0.1:5000/api/entries', data, {
          headers: { Authorization: `Bearer ${token}` },
          timeout: 5000
        })
        message.value = 'Ieraksts saglabāts!'
      } else {
        message.value = 'Ieraksts saglabāts lokāli.'
      }
      setTimeout(() => emit('saved'), 1500)
    } catch (syncErr) {
      console.warn('EntryForm: Sync failed but data is saved locally', syncErr)
      message.value = 'Saglabāts lokāli (gaida sinhronizāciju).'
      setTimeout(() => emit('saved'), 2000)
    }
  } catch (dbErr) {
    console.error('EntryForm: CRITICAL - Dexie addEntry failed:', dbErr)
    message.value = 'Kļūda saglabājot lokāli! Lūdzu, mēģiniet vēlreiz.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="entry-form animate-fade-in">
    <div class="header-row">
      <button @click="$emit('saved')" class="btn-text">
        <ChevronLeft :size="20" /> Atpakaļ
      </button>
      <input v-model="date" type="date" class="date-picker" />
    </div>

    <div class="glass-card">
      <section class="form-section">
        <h3><Sun :size="20" color="#f59e0b" /> 3 Labas lietas</h3>
        <div v-for="(item, i) in positiveThings" :key="'pos-'+i" class="input-group">
          <input v-model="positiveThings[i]" placeholder="Kas tevi šodien iepriecināja?" />
        </div>
      </section>

      <section class="form-section">
        <h3><Cloud :size="20" color="#64748b" /> Negatīvās lietas (neobligāti)</h3>
        <div v-for="(item, i) in negativeThings" :key="'neg-'+i" class="input-group">
          <input v-model="negativeThings[i]" placeholder="Kas šodien neizdevās?" />
        </div>
        <button v-if="negativeThings.length < 3" @click="addField(negativeThings)" class="btn-plus">+ Pievienot vēl vienu</button>
      </section>

      <section class="form-section">
        <h3><Heart :size="20" color="#ec4899" /> Pateicības</h3>
        <div v-for="(item, i) in gratitude" :key="'grat-'+i" class="input-group">
          <input v-model="gratitude[i]" placeholder="Par ko tu šodien jūties pateicīgs?" />
        </div>
        <button v-if="gratitude.length < 3" @click="addField(gratitude)" class="btn-plus">+ Pievienot vēl vienu</button>
      </section>

      <section class="form-section">
        <h3>Emocijas</h3>
        <div class="emotion-cloud">
          <button 
            v-for="emotion in defaultEmotions" 
            :key="emotion"
            @click="toggleEmotion(emotion)"
            :class="{ active: emotions.includes(emotion) }"
            class="emotion-tag"
          >
            {{ emotion }}
          </button>
        </div>
      </section>

      <section class="form-section">
        <h3>Piezīmes un Dienasgrāmata</h3>
        <textarea v-model="diaryEntry" rows="5" placeholder="Pastāsti plašāk par savu dienu..."></textarea>
      </section>

      <div class="actions">
        <p v-if="message" class="status-msg">{{ message }}</p>
        <button @click="saveEntry" class="btn btn-primary" :disabled="loading">
          <Save :size="20" /> {{ loading ? 'Saglabā...' : 'Saglabāt dienu' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.entry-form {
  max-width: 800px;
  margin: 0 auto;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.date-picker {
  width: auto;
  font-weight: 600;
  border: none;
  background: transparent;
  color: var(--primary);
}

.form-section {
  margin-bottom: 2.5rem;
}

.form-section h3 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.25rem;
  border-bottom: 1px solid rgba(0,0,0,0.05);
  padding-bottom: 0.5rem;
}

.btn-plus {
  background: transparent;
  border: none;
  color: var(--primary);
  font-weight: 500;
  cursor: pointer;
  padding: 0.5rem;
}

.emotion-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
}

.emotion-tag {
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0,0,0,0.1);
  padding: 0.5rem 1rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}

.emotion-tag:hover {
  background: white;
  border-color: var(--primary);
}

.emotion-tag.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
  transform: scale(1.05);
}

.actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.status-msg {
  color: var(--success);
  font-weight: 600;
}

.btn-text {
  background: transparent;
  border: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  cursor: pointer;
  font-family: inherit;
}
</style>
