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

  </v-app>
</template>

<script setup>
import Dashboard from './dashboard.vue'
import Toolbar from './toolbar.vue'
import RentalsList from './rentals.vue'
</script>
