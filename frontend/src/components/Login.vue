<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { syncData } from '../services/sync'

const emit = defineEmits(['login-success'])

const isRegister = ref(false)
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const BASE_URL = 'http://127.0.0.1:5000/api'

const handleSubmit = async () => {
  loading.value = true
  error.value = ''
  try {
    if (isRegister.value) {
      await axios.post(`${BASE_URL}/auth/register`, {
        username: username.value,
        password: password.value
      })
      // Auto-login after registration
      const response = await axios.post(`${BASE_URL}/auth/login`, {
        username: username.value,
        password: password.value
      })
      await syncData()
      emit('login-success', response.data)
    } else {
      const response = await axios.post(`${BASE_URL}/auth/login`, {
        username: username.value,
        password: password.value
      })
      await syncData()
      emit('login-success', response.data)
    }
  } catch (err) {
    error.value = err.response?.data?.message || 'Notika kļūda. Mēģiniet vēlreiz.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="glass-card login-card animate-fade-in">
      <h2>{{ isRegister ? 'Izveidot kontu' : 'Ienākt' }}</h2>
      <p class="subtitle">Trīs Labas Lietas — Tavas pašsajūtas dienasgrāmata</p>
      
      <form @submit.prevent="handleSubmit">
        <div class="input-group">
          <label>Lietotājvārds</label>
          <input v-model="username" type="text" required placeholder="Tavs vārds" />
        </div>
        
        <div class="input-group">
          <label>Parole</label>
          <input v-model="password" type="password" required placeholder="********" />
        </div>
        
        <p v-if="error" class="error-msg">{{ error }}</p>
        
        <button type="submit" class="btn btn-primary w-full" :disabled="loading">
          {{ loading ? 'Gaidi...' : (isRegister ? 'Reģistrēties' : 'Ienākt') }}
        </button>
      </form>
      
      <div class="toggle-auth">
        <button @click="isRegister = !isRegister" class="text-btn">
          {{ isRegister ? 'Jau ir konts? Ienākt' : 'Nav konta? Reģistrēties' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.login-card {
  width: 100%;
  max-width: 400px;
  text-align: center;
}

h2 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: var(--text-muted);
  margin-bottom: 2rem;
}

.error-msg {
  color: var(--error);
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.w-full {
  width: 100%;
  justify-content: center;
}

.toggle-auth {
  margin-top: 1.5rem;
}

.text-btn {
  background: transparent;
  border: none;
  color: var(--primary);
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
}

.text-btn:hover {
  text-decoration: underline;
}
</style>
