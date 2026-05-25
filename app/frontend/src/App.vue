<template>
  <div id="app" class="app">
    <header class="header">
      <h1>Hoop It Up</h1>
      <p class="subtitle">Can you play today?</p>
    </header>

    <main class="main">
      <div v-if="!connected" class="status connecting">
        <p>Connecting...</p>
      </div>

      <div v-else class="container">
        <!-- Vote Buttons -->
        <div class="vote-section">
          <button
            @click="submitVote('yes')"
            class="btn btn-yes"
            :class="{ active: playerVote === 'yes' }"
          >
            👍 Yes
          </button>

          <button
            @click="submitVote('yes_if_3')"
            class="btn btn-yes"
            :class="{ active: playerVote === 'yes_if_3' }"
          >
            👍 Yes (if enough for 3's)
          </button>

          <button
            @click="submitVote('yes_if_5')"
            class="btn btn-yes"
            :class="{ active: playerVote === 'yes_if_5' }"
          >
            👍 Yes (if enough for 5's)
          </button>

          <button
            @click="submitVote('maybe')"
            class="btn btn-maybe"
            :class="{ active: playerVote === 'maybe' }"
          >
            ❓ Maybe
          </button>

          <button
            @click="submitVote('no')"
            class="btn btn-no"
            :class="{ active: playerVote === 'no' }"
          >
            👎 No
          </button>
        </div>

        <!-- Vote Results -->
        <div class="results">
          <div class="result-card yes">
            <span class="count">{{ votes.yes }}</span>
            <span class="label">Yes</span>
          </div>
          <div class="result-card yes-if">
            <span class="count">{{ votes.yes_if_3 }}</span>
            <span class="label">Yes (if 3's)</span>
          </div>
          <div class="result-card yes-if">
            <span class="count">{{ votes.yes_if_5 }}</span>
            <span class="label">Yes (if 5's)</span>
          </div>
          <div class="result-card maybe">
            <span class="count">{{ votes.maybe }}</span>
            <span class="label">Maybe</span>
          </div>
          <div class="result-card no">
            <span class="count">{{ votes.no }}</span>
            <span class="label">No</span>
          </div>
        </div>

        <!-- Game Status -->
        <div class="status-info">
          <p class="total">Total Responses: <strong>{{ votes.total }}</strong></p>
          <p class="thresholds">
            <strong>3v3 ready:</strong>
            <span :class="{ ready: votes.enough_for_3 }">{{ votes.enough_for_3 ? 'Yes' : 'No' }}</span>
            &nbsp;•&nbsp;
            <strong>5v5 ready:</strong>
            <span :class="{ ready: votes.enough_for_5 }">{{ votes.enough_for_5 ? 'Yes' : 'No' }}</span>
          </p>
        </div>

        <!-- Reset Button -->
        <button @click="resetVotes" class="btn btn-reset">
          Reset Votes
        </button>
      </div>
    </main>

    <footer class="footer">
      <p>Check back later to see if there's a game today!</p>
    </footer>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import io from 'socket.io-client'

export default {
  name: 'App',
  setup() {
    const socket = ref(null)
    const connected = ref(false)
    const playerVote = ref(null)
    const votes = ref({
      yes: 0,
      yes_if_3: 0,
      yes_if_5: 0,
      no: 0,
      maybe: 0,
      total: 0,
      enough_for_3: false,
      enough_for_5: false
    })

    const gameStatus = computed(() => {
      if (votes.value.yes + votes.value.yes_if_3 > votes.value.no) {
        return 'ON'
      } else if (votes.value.no > votes.value.yes + votes.value.yes_if_3) {
        return 'OFF'
      } else {
        return 'UNDECIDED'
      }
    })

    const submitVote = (choice) => {
      playerVote.value = choice
      if (socket.value) {
        socket.value.emit('vote', { vote: choice })
        notifyUser('Vote Recorded', { body: `You voted: ${choice}` })
      }
    }

    const resetVotes = () => {
      if (socket.value && confirm('Reset all votes?')) {
        socket.value.emit('reset_votes')
        playerVote.value = null
      }
    }

    const notifyUser = (title, options = {}) => {
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
          icon: '/icon-192x192.png',
          ...options
        })
      }
    }

    const requestNotificationPermission = async () => {
      if ('Notification' in window && Notification.permission === 'default') {
        try {
          const permission = await Notification.requestPermission()
          if (permission === 'granted') {
            console.log('Notification permission granted')
          }
        } catch (error) {
          console.error('Error requesting notification permission:', error)
        }
      }
    }

    onMounted(() => {
      requestNotificationPermission()

      const protocol = window.location.protocol === 'https:' ? 'https' : 'http'
      const url = `${protocol}://${window.location.hostname}:${window.location.port || (protocol === 'https' ? 443 : 80)}`

      socket.value = io(url, {
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: 5
      })

      socket.value.on('connect', () => {
        connected.value = true
        console.log('Connected to server')
      })

      socket.value.on('disconnect', () => {
        connected.value = false
        console.log('Disconnected from server')
      })

      socket.value.on('votes_update', (data) => {
        votes.value = Object.assign({}, votes.value, data)
        if (data.total > 0) {
          notifyUser('Vote Update', {
            body: `Yes: ${data.yes} (+${data.yes_if_3} if 3's, +${data.yes_if_5} if 5's) | No: ${data.no} | Maybe: ${data.maybe}`,
            tag: 'votes-update',
            requireInteraction: false
          })
        }
      })

      socket.value.on('scheduled_message', (data) => {
        console.log('Scheduled message received:', data)
        notifyUser('Game Announcement', {
          body: data.message,
          tag: 'scheduled-message',
          requireInteraction: true
        })
      })
    })

    onUnmounted(() => {
      if (socket.value) {
        socket.value.disconnect()
      }
    })

    return {
      connected,
      playerVote,
      votes,
      gameStatus,
      submitVote,
      resetVotes
    }
  }
}
</script>

<style scoped>
/* Keep the original styles (trimmed for brevity) */
/* Reuse the previous stylesheet in the repo; add a small style for ready */
.result-card.yes-if { background: linear-gradient(135deg, #2ecc71, #27ae60); }
.thresholds .ready { color: #27AE60; font-weight: 700; }
</style>
