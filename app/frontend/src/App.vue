<template>
  <div id="app" class="container py-3">
    <header class="d-flex flex-column align-items-center mb-3">
      <h1 class="h3 mb-0">Hoop It Up</h1>
      <p class="text-muted small">Can you play today?</p>
    </header>

    <main>
      <div v-if="!connected" class="text-center py-5">
        <div class="spinner-border text-secondary" role="status">
          <span class="visually-hidden">Connecting...</span>
        </div>
        <p class="mt-2">Connecting...</p>
      </div>

      <div v-else>
        <!-- Vote Buttons -->
        <div class="vote-section mb-3">
          <div class="row g-2">
            <div class="col-1 col-md-1 d-none d-md-block" aria-hidden="true">
              &nbsp;
            </div>
            <div
              class="col-6 col-sm-6 col-md-2"
              v-for="btn in voteButtons"
              :key="btn.key"
            >
              <button
                @click="submitVote(btn.key)"
                class="btn w-100"
                :class="{
                  'btn-outline-success':
                    btn.style === 'success' && playerVote !== btn.key,
                  'btn-success':
                    btn.style === 'success' && playerVote === btn.key,
                  'btn-outline-warning':
                    btn.style === 'warning' && playerVote !== btn.key,
                  'btn-warning':
                    btn.style === 'warning' && playerVote === btn.key,
                  'btn-outline-danger':
                    btn.style === 'danger' && playerVote !== btn.key,
                  'btn-danger':
                    btn.style === 'danger' && playerVote === btn.key,
                }"
              >
                {{ btn.label }}
              </button>
            </div>
            <div class="col-1 col-md-1 d-none d-md-block" aria-hidden="true">
              &nbsp;
            </div>
          </div>
        </div>

        <!-- Game Status -->
        <div class="status mb-3 mt-5">
          <div class="row g-2 text-center">
            <div class="col-1 col-md-1 d-none d-md-block" aria-hidden="true">
              &nbsp;
            </div>
            <div class="col-12 col-sm-12 col-md-10" title="Results">
              <div class="status-info text-center">
                <div class="p-2 rounded bg-transparent border border-secondary">
                  <div class="h4 mb-0">
                    <strong>{{ expected }}</strong>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-1 col-md-1 d-none d-md-block" aria-hidden="true">
              &nbsp;
            </div>
          </div>
        </div>

        <!-- Vote Results -->
        <div class="results mb-3">
          <div class="row">
            <div class="col-1 col-md-1 d-none d-md-block" aria-hidden="true">
              &nbsp;
            </div>
            <div class="col-12 col-md-10" title="Current Votes">
              <div class="h5 mb-0">Responses:</div>
            </div>
            <div class="col-1 col-md-1 d-none d-md-block" aria-hidden="true">
              &nbsp;
            </div>
          </div>
          <div class="row g-2 text-center">
            <div class="col-1 col-md-1 d-none d-md-block" aria-hidden="true">
              &nbsp;
            </div>
            <div class="col-6 col-sm-4 col-md-2" title="Yes">
              <div class="p-2 rounded bg-light">
                <div class="h4 mb-0">{{ votes.yes }}</div>
                <small>Yes</small>
              </div>
            </div>
            <div class="col-6 col-sm-4 col-md-2" title="Yes (if 3's)">
              <div class="p-2 rounded bg-success text-white">
                <div class="h4 mb-0">{{ votes.yes_if_3 }}</div>
                <small>Yes (if 3's)</small>
              </div>
            </div>
            <div class="col-6 col-sm-4 col-md-2" title="Yes (if 5's)">
              <div class="p-2 rounded bg-success text-white">
                <div class="h4 mb-0">{{ votes.yes_if_5 }}</div>
                <small>Yes (if 5's)</small>
              </div>
            </div>
            <div class="col-6 col-sm-4 col-md-2" title="Maybe">
              <div class="p-2 rounded bg-warning">
                <div class="h4 mb-0">{{ votes.maybe }}</div>
                <small>Maybe</small>
              </div>
            </div>
            <div class="col-6 col-sm-4 col-md-2" title="No">
              <div class="p-2 rounded bg-light">
                <div class="h4 mb-0">{{ votes.no }}</div>
                <small>No</small>
              </div>
            </div>
            <div class="col-1 col-md-1 d-none d-md-block" aria-hidden="true">
              &nbsp;
            </div>
          </div>
        </div>
        <div class="fixed-bottom">
            <p class="text-muted">Version {{ version }}</p>
        </div>
      </div>
    </main>

    <footer class="footer text-center mt-4">
      <p>{{ summary }}</p>
    </footer>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { computeExpectedValue } from "./utils/expectedValue.cjs";
import io from "socket.io-client";
import axios from "axios";

export default {
  name: "App",
  setup() {
    const socket = ref(null);
    const connected = ref(false);
    const playerVote = ref(null);
    const votes = ref({
      yes: 0,
      yes_if_3: 0,
      yes_if_5: 0,
      no: 0,
      maybe: 0,
    });
    const version = __APP_VERSION__

    const expected = computed(() => computeExpectedValue(votes.value));

    const summary = computed(() => {
      if (expected.value.startsWith("No game yet")) {
        return "Check back later to see if there's a game today!";
      } else {
        return "";
      }
    });

    const submitVote = (choice) => {
      playerVote.value = choice;
      if (socket.value) {
        socket.value.emit("vote", { vote: choice });
      }
    };

    const notifyUser = (title, options = {}) => {
      if ("Notification" in window && Notification.permission === "granted") {
        new Notification(title, {
          icon: "/icon-192x192.png",
          ...options,
        });
      }
    };

    const requestNotificationPermission = async () => {
      if ("Notification" in window && Notification.permission === "default") {
        try {
          const permission = await Notification.requestPermission();
          if (permission === "granted") {
            console.log("Notification permission granted");
          }
        } catch (error) {
          console.error("Error requesting notification permission:", error);
        }
      }
    };

    onMounted(() => {
      requestNotificationPermission();

      // Restore this user's previous vote (if any)
      const fetchCurrentVote = async () => {
        try {
          const resp = await axios.get("/api/current-vote");
          if (resp && resp.data && resp.data.vote) {
            playerVote.value = resp.data.vote;
            console.log("Restored previous vote:", resp.data.vote);
          }
        } catch (err) {
          console.warn("Could not fetch current vote:", err);
        }
      };
      fetchCurrentVote();

      const protocol = window.location.protocol === "https:" ? "https" : "http";
      const url = `${protocol}://${window.location.hostname}:${
        window.location.port || (protocol === "https" ? 443 : 80)
      }`;

      socket.value = io(url, {
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: 5,
      });

      socket.value.on("connect", () => {
        connected.value = true;
        console.log("Connected to server");
      });

      socket.value.on("disconnect", () => {
        connected.value = false;
        console.log("Disconnected from server");
      });

      socket.value.on("votes_update", (data) => {
        console.log("Votes update received:", data);
        votes.value = Object.assign({}, votes.value, data);
      });

      socket.value.on("daily_summary", (data) => {
        console.log("Daily summary received:", data);
        votes.value = Object.assign({}, votes.value, data);
        var title = "Game on!";
        var message = "Looks like we have " + expected.value + " today!";
        if (expected.value.startsWith("No game yet")) {
          title = "Looks like no game today.";
          message = expected.value.replace(" yet ", " ");
        }
        notifyUser(title, {
          body: message,
          tag: "daily-summary",
          requireInteraction: true,
        });
      });

      socket.value.on("scheduled_message", (data) => {
        console.log("Scheduled message received:", data);
        notifyUser("Game Today?", {
          body: data.message,
          tag: "game-today?",
          requireInteraction: true,
        });
      });
    });

    onUnmounted(() => {
      if (socket.value) {
        socket.value.disconnect();
      }
    });

    const voteButtons = [
      { key: "yes", label: "👍 Yes", style: "success" },
      { key: "yes_if_3", label: "👍 Yes (if 3's)", style: "success" },
      { key: "yes_if_5", label: "👍 Yes (if 5's)", style: "success" },
      { key: "maybe", label: "❓ Maybe", style: "warning" },
      { key: "no", label: "👎 No", style: "danger" },
    ];

    return {
      connected,
      playerVote,
      votes,
      submitVote,
      expected,
      summary,
      voteButtons,
      version,
    };
  },
};
</script>

<style scoped>
/* Keep the original styles (trimmed for brevity) */
/* Reuse the previous stylesheet in the repo; add a small style for ready */

.thresholds .ready {
  color: #27ae60;
  font-weight: 700;
}

/* Ensure headings render light over the dark background */
h1,
h2,
h3,
h4,
h5,
h6 {
  color: var(--bs-heading-color, #f5f7fa);
}

h1 {
  font-size: 2rem;
}

/* Make muted text readable on dark background */
.text-muted {
  color: rgba(245, 247, 250, 0.65) !important;
}

/* Ensure general app text is light */
#app,
#app p,
#app small,
#app .status-info,
#app .footer {
  color: #f5f7fa;
}

/* Result cards: force a gray background at 50% opacity */
.results .p-2 {
  background-color: rgba(128, 128, 128, 0.5) !important;
  border-color: rgba(128, 128, 128, 0.5) !important;
}

.btn-warning {
  --bs-btn-hover-bg: #977307 !important;
  --bs-btn-bg: #d4a004 !important;
}

/* Non-active (outline) vote buttons: give them a 50% transparent background
   matching their semantic color while keeping readable text. Active solid
   buttons keep their normal appearance. */
.vote-section .btn {
  color: #fff !important;
}
.vote-section .btn.btn-outline-success {
  background-color: rgba(45, 45, 45, 0.8) !important;
  border-color: rgba(25, 135, 84, 0.75) !important;
}
.vote-section .btn.btn-outline-warning {
  background-color: rgba(45, 45, 45, 0.8) !important;
  border-color: rgba(255, 193, 7, 0.75) !important;
}
.vote-section .btn.btn-outline-danger {
  background-color: rgba(45, 45, 45, 0.8) !important;
  border-color: rgba(220, 53, 69, 0.75) !important;
}

/* Ensure solid/active buttons remain fully colored and legible */
.vote-section .btn.btn-success,
.vote-section .btn.btn-warning,
.vote-section .btn.btn-danger {
  color: #fff;
}
</style>
