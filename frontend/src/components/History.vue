<script setup>
import { ref, onMounted } from 'vue'
import { Calendar, Trash2, ChevronRight, Search } from 'lucide-vue-next'
import { getEntries, deleteEntry } from '../db'
import { syncData } from '../services/sync'
import axios from 'axios'

const entries = ref([])
const loading = ref(true)
const searchQuery = ref('')
const BASE_URL = 'http://127.0.0.1:5000/api'

onMounted(async () => {
  // Load local entries immediately for fast UI
  await loadEntries()
  
  // Start sync in background
  syncData().then(() => {
    // Refresh list if sync could have added new items
    loadEntries()
  }).catch(err => {
    console.warn('Sync failed in background, using local data only', err)
  })
})

const loadEntries = async (forceSync = false) => {
  loading.value = true
  try {
    if (forceSync) {
      console.log('History: Manual sync requested');
      await syncData()
    }
    // Load from local DB
    const localEntries = await getEntries()
    entries.value = localEntries
  } catch (err) {
    console.error('History: Failed to load entries:', err)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleDateString('lv-LV', { 
    day: 'numeric', 
    month: 'long', 
    year: 'numeric' 
  })
}

const handleDelete = async (entry) => {
  if (!confirm('Vai tiešām vēlaties dzēst šo ierakstu?')) return
  
  try {
    // Delete locally
    await deleteEntry(entry.id)
    
    // Attempt remote delete
    const token = localStorage.getItem('token')
    if (token && entry.id) {
      await axios.delete(`${BASE_URL}/entries/${entry.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
    }
    
    // Refresh list
    await loadEntries()
  } catch (err) {
    console.error('Delete failed:', err)
  }
}
</script>

<template>
  <div class="history-view animate-fade-in">
    <div class="view-header">
      <div class="header-main">
        <h2><Calendar :size="28" /> Tavu ierakstu vēsture</h2>
        <p>Šeit tu vari atrast visus savus iepriekšējos pierakstus.</p>
      </div>
      <button @click="loadEntries(true)" class="btn btn-secondary btn-sm" :disabled="loading">
        <Search :size="16" /> Atsvaidzināt
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <p>Ielādē ierakstus...</p>
    </div>

    <div v-else-if="entries && entries.length" class="history-list">
      <div v-for="entry in entries" :key="entry.id || entry.date" class="glass-card entry-item">
        <div class="entry-main">
          <div class="entry-date">{{ formatDate(entry.date) }}</div>
          <div class="entry-content">
            <div v-if="entry.emotions && entry.emotions.length" class="tags">
              <span v-for="em in entry.emotions" :key="em" class="badge">{{ em }}</span>
            </div>
            <p v-if="entry.positive_things && entry.positive_things.length" class="preview-text">
              ✨ {{ entry.positive_things[0] }}...
            </p>
          </div>
        </div>
        <div class="entry-actions">
          <button @click="handleDelete(entry)" class="btn-icon delete" title="Dzēst">
            <Trash2 :size="18" />
          </button>
        </div>
      </div>
    </div>

    <div v-else class="empty-state glass-card">
      <p>Nav atrasts neviens ieraksts. Sāc rakstīt šodien!</p>
    </div>
  </div>
</template>

<style scoped>
.history-view {
  max-width: 900px;
  margin: 0 auto;
  padding: 1rem;
}

.view-header {
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.header-main {
  flex: 1;
}

.view-header h2 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.view-header p {
  color: var(--text-muted);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.entry-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  transition: transform 0.2s ease;
}

.entry-item:hover {
  transform: translateX(5px);
}

.entry-date {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 0.5rem;
}

.preview-text {
  color: var(--text-muted);
  font-style: italic;
  margin-top: 0.5rem;
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
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  color: var(--text-muted);
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.5);
}

.btn-icon.delete:hover {
  color: var(--error);
}

.empty-state {
  text-align: center;
  padding: 5rem 2rem;
}
</style>
