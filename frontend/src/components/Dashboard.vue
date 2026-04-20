<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { PlusCircle, Info, TrendingUp, Calendar as CalendarIcon, Trash2, Edit2 } from 'lucide-vue-next'
import { getEntries, deleteEntry } from '../db'

const emit = defineEmits(['open-form'])

const entries = ref([])
const recommendations = ref([])
const loading = ref(true)

const BASE_URL = 'http://127.0.0.1:5000/api'

onMounted(async () => {
  await loadData()
})

const loadData = async () => {
  loading.value = true
  // 1. Load from local DB
  try {
    entries.value = await getEntries()
    console.log('Loaded entries:', entries.value)
  } catch (err) {
    console.error('Dexie getEntries failed:', err)
  }
  
  // 2. Try to load from API
  const token = localStorage.getItem('token')
  if (token) {
    try {
      const resp = await axios.get(`${BASE_URL}/recommendations`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      recommendations.value = resp.data
    } catch (err) {
      console.warn('Could not load recommendations', err)
      recommendations.value = [{ type: 'offline', message: 'Esi bezsaistē. Sinhronizācija būs pieejama vēlāk!' }]
    }
  }
  loading.value = false
}

const handleDelete = async (entry) => {
  if (!confirm('Vai tiešām vēlaties dzēst šīs dienas ierakstu?')) return

  try {
    // 1. Local delete
    await deleteEntry(entry.id)
    
    // 2. Remote delete
    const token = localStorage.getItem('token')
    if (token && entry.id) {
        await axios.delete(`${BASE_URL}/entries/${entry.id}`, {
            headers: { Authorization: `Bearer ${token}` }
        })
    }
    
    // Refresh list
    await loadData()
  } catch (err) {
    console.error('Failed to delete entry:', err)
    alert('Kļūda dzēšot ierakstu.')
  }
}

const formatDate = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleDateString('lv-LV', { day: 'numeric', month: 'long' })
}
</script>

<template>
  <div class="dashboard">
    <!-- Recommendations Section -->
    <div v-if="recommendations.length" class="recommendations">
      <div v-for="rec in recommendations" :key="rec.message" class="glass-card recommendation-card animate-fade-in">
        <div class="rec-icon">
          <Info v-if="rec.type === 'vispārīgs'" :size="32" color="#8b5cf6" />
          <TrendingUp v-else :size="32" color="#10b981" />
        </div>
        <div class="rec-content">
          <p>{{ rec.message }}</p>
        </div>
      </div>
    </div>

    <div class="stats-row">
      <div class="glass-card stat-card">
        <div class="stat-icon"><PlusCircle :size="24" /></div>
        <div class="stat-info">
          <h3>Šodienas progress</h3>
          <p>Vai esi jau pierakstījis 3 labas lietas?</p>
          <button @click="$emit('open-form')" class="btn btn-primary btn-sm">Sākt tagad</button>
        </div>
      </div>
    </div>

    <h2><CalendarIcon :size="24" /> Pēdējie ieraksti</h2>
    
    <div v-if="entries.length" class="entries-list">
      <div v-for="entry in entries" :key="entry.date" class="glass-card entry-row animate-fade-in">
        <div class="entry-date">{{ formatDate(entry.date) }}</div>
        <div class="entry-preview">
          <div class="pos-preview">
            <span v-for="(p, i) in entry.positive_things.slice(0, 3)" :key="i" class="dot"></span>
          </div>
          <div class="emotions-preview">
            <span v-for="em in entry.emotions.slice(0, 3)" :key="em" class="badge">{{ em }}</span>
          </div>
        </div>
        <button @click="$emit('open-form')" class="btn-icon">✏️</button>
      </div>
    </div>
    
    <div v-else-if="!loading" class="empty-state glass-card">
      <p>Tev vēl nav neviena ieraksta. Sāc savu labsajūtas ceļojumu šodien!</p>
      <button @click="$emit('open-form')" class="btn btn-primary">Pievienot pirmo ierakstu</button>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.recommendations {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.recommendation-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  border-left: 4px solid var(--primary);
}

.rec-content p {
  font-weight: 500;
  line-height: 1.4;
}

.stat-card {
  display: flex;
  gap: 1.5rem;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(255, 255, 255, 0.4) 100%);
}

.stat-icon {
  background: white;
  padding: 1rem;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.entries-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.entry-row {
  display: grid;
  grid-template-columns: 150px 1fr auto;
  align-items: center;
  padding: 1rem 1.5rem;
  margin-bottom: 0;
}

.entry-date {
  font-weight: 600;
  color: var(--text-muted);
}

.entry-preview {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.pos-preview {
  display: flex;
  gap: 4px;
}

.dot {
  width: 10px;
  height: 10px;
  background: var(--success);
  border-radius: 50%;
}

.badge {
  background: rgba(139, 92, 246, 0.1);
  color: var(--primary);
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  margin-right: 0.5rem;
}

.btn-icon {
  background: transparent;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-state p {
  margin-bottom: 2rem;
  color: var(--text-muted);
}

@media (max-width: 600px) {
  .entry-row {
    grid-template-columns: 1fr auto;
    gap: 0.5rem;
  }
  .entry-preview {
    grid-column: 1 / span 2;
    margin-top: 0.5rem;
  }
}
</style>
