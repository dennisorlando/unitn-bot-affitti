<template>
  <v-container fluid class="d-flex justify-center align-center py-10">
    <v-row justify="center" align="center" class="text-center" no-gutters>
      <!-- Synched Messages -->
      <v-col cols="12" sm="6" md="4" class="d-flex justify-center">
        <div class="circle blue-border">
          <div class="circle-content">
            <div class="circle-text">{{ synched }}</div>
            <div class="circle-label text-blue-darken-2">
              Synched<br />messages
            </div>
          </div>
        </div>
      </v-col>

      <!-- Processed Messages -->
      <v-col cols="12" sm="6" md="4" class="d-flex justify-center">
        <div class="circle green-border">
          <div class="circle-content">
            <div class="circle-text">{{ processed }}</div>
            <div class="circle-label text-green-darken-2">
              Processed<br />messages
            </div>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const synched = ref(0)
const processed = ref(0)

async function updateData() {
  try {
    const [synchedRes, processedRes] = await Promise.all([
      fetch('http://localhost:9009/messages/count/total'),
      fetch('http://localhost:9009/messages/count/processed')
    ]);

    const synchedData = await synchedRes.json();
    const processedData = await processedRes.json();

    synched.value = synchedData.count;
    processed.value = processedData.count;
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}

onMounted(() => {
  updateData()
  setInterval(updateData, 5000)
})
</script>

<style scoped>
.circle {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  border-width: 20px;
  border-style: solid;
  text-align: center;
}

.blue-border {
  border-color: #1976d2; /* Material Blue 700 */
}

.green-border {
  border-color: #388e3c; /* Material Green 700 */
}

.circle-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  line-height: 1.2;
}

.circle-text {
  font-size: 2.5rem;
  font-weight: bold;
  color: #424242;
}

.circle-label {
  font-size: 0.9rem;
  font-weight: 500;
}
</style>
