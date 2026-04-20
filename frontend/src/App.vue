<script setup>
import { ref, onMounted } from 'vue'
import { Plus, LayoutDashboard, History, Settings, LogOut } from 'lucide-vue-next'
import Dashboard from './components/Dashboard.vue'
import EntryForm from './components/EntryForm.vue'
import Login from './components/Login.vue'
import HistoryView from './components/History.vue'

const currentView = ref('dashboard')
const user = ref(null)
const token = ref(localStorage.getItem('token'))
const selectedDate = ref(null)

onMounted(() => {
  const savedUser = localStorage.getItem('username')
  if (savedUser && token.value) {
    user.value = { username: savedUser }
  }
})

const openForm = (date = null) => {
  selectedDate.value = date || new Date().toISOString().split('T')[0]
  currentView.value = 'form'
}

const handleLogin = (data) => {
  token.value = data.token
  user.value = { username: data.username }
  localStorage.setItem('token', data.token)
  localStorage.setItem('username', data.username)
  currentView.value = 'dashboard'
}

const logout = () => {
  token.value = null
  user.value = null
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  currentView.value = 'login'
}

if (!token.value) {
  currentView.value = 'login'
}
</script>

<template>
  <div class="app-container">
    <header v-if="token" class="glass-card nav-header">
      <div class="logo">
        <h1>✨ Trīs Labas Lietas</h1>
      </div>
      <nav>
        <button @click="currentView = 'dashboard'" :class="{ active: currentView === 'dashboard' }" class="nav-btn">
          <LayoutDashboard :size="20" /> Ieskatam
        </button>
        <button @click="openForm()" :class="{ active: currentView === 'form' }" class="nav-btn">
          <Plus :size="20" /> Jauns Ieraksts
        </button>
        <button @click="currentView = 'history'" :class="{ active: currentView === 'history' }" class="nav-btn">
          <History :size="20" /> Vēsture
        </button>
        <button @click="logout" class="nav-btn logout">
          <LogOut :size="20" /> Iziet
        </button>
      </nav>
    </header>

    <main class="animate-fade-in">
      <Login v-if="currentView === 'login'" @login-success="handleLogin" />
      <Dashboard v-else-if="currentView === 'dashboard'" @open-form="openForm" />
      <HistoryView v-else-if="currentView === 'history'" />
      <EntryForm v-else-if="currentView === 'form'" :initial-date="selectedDate" @saved="currentView = 'dashboard'" />
    </main>

    <footer v-if="token">
      <p>© 2026 Trīs Labas Lietas — Tavs labsajūtas ceļvedis</p>
    </footer>
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  margin-top: 1rem;
}

nav {
  display: flex;
  gap: 1rem;
}

.nav-btn {
  background: transparent;
  border: none;
  font-family: inherit;
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.4);
  color: var(--primary);
}

.nav-btn.active {
  background: white;
  color: var(--primary);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.logout:hover {
  color: var(--error);
}

main {
  flex: 1;
}

footer {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .nav-header {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
