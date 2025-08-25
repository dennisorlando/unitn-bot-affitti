<template>
  <v-app>
    <v-container fluid>
      <v-row>
        <v-col>
          <Dashboard />
        </v-col>
      </v-row>

      <v-row>
        <v-col>
          <Toolbar />
        </v-col>
      </v-row>

      <v-row>
        <v-col>
          <RentalsList />
        </v-col>
      </v-row>
    </v-container>

    <v-btn
      class="ma-4"
      color="primary"
      icon="mdi-cog"
      size="large"
      fixed
      bottom
      right
      @click="settingsDialog = true"
    ></v-btn>

    <SettingsDialog v-model="settingsDialog" />
  </v-app>
</template>

<script setup>
import { ref } from 'vue';
import Dashboard from './dashboard.vue';
import Toolbar from './toolbar.vue';
import RentalsList from './rentals.vue';
import SettingsDialog from './SettingsDialog.vue';

const settingsDialog = ref(false);
</script>
