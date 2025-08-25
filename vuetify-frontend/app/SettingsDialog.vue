<template>
  <v-dialog v-model="dialog" max-width="600px">
    <v-card>
      <v-card-title class="headline">Settings</v-card-title>
      <v-card-text>
        <v-list dense>
          <v-list-item v-if="loading">
            <v-list-item-content>
              <v-list-item-title>Loading chats...</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item v-else-if="chats.length === 0">
            <v-list-item-content>
              <v-list-item-title>No active chats found.</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item v-for="chat in chats" :key="chat.id">
            <v-list-item-content>
              <v-list-item-title>{{ chat.name }}</v-list-item-title>
            </v-list-item-content>
            <v-list-item-action>
              <v-btn icon @click="removeChat(chat.id)">
                <v-icon color="error">mdi-delete</v-icon>
              </v-btn>
            </v-list-item-action>
          </v-list-item>
        </v-list>

        <v-text-field
          v-model="newChatName"
          label="New Chat Name"
          outlined
          dense
          class="mt-4"
        ></v-text-field>
        <v-btn color="primary" @click="addChat" :disabled="!newChatName.trim() || loading">
          Add Chat
        </v-btn>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="dialog = false">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';

const props = defineProps({
  modelValue: Boolean,
});

const emit = defineEmits(['update:modelValue']);

const dialog = ref(props.modelValue);
const chats = ref([]);
const newChatName = ref('');
const loading = ref(false);

const fetchChats = async () => {
  loading.value = true;
  try {
    // Placeholder for API call to fetch active chats
    // Replace with actual API endpoint
    const response = await fetch('http://localhost:9009/active_chats');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    // The backend returns { "chat_names": [...] }
    chats.value = data.chat_names.map(name => ({ id: name, name: name }));
  } catch (error) {
    console.error("Error fetching chats:", error);
    // Optionally, display an error message to the user
  } finally {
    loading.value = false;
  }
};

const addChat = async () => {
  if (!newChatName.value.trim()) return;
  loading.value = true;
  try {
    // Placeholder for API call to add a chat
    // Replace with actual API endpoint
    const response = await fetch('http://localhost:9009/active_chats', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name: newChatName.value }),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    newChatName.value = ''; // Clear input
    await fetchChats(); // Refresh list
  } catch (error) {
    console.error("Error adding chat:", error);
    // Optionally, display an error message to the user
  } finally {
    loading.value = false;
  }
};

const removeChat = async (chatId) => {
  loading.value = true;
  try {
    // Placeholder for API call to remove a chat
    // Replace with actual API endpoint
    const response = await fetch(`http://localhost:9009/active_chats/${chatId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    await fetchChats(); // Refresh list
  } catch (error) {
    console.error("Error removing chat:", error);
    // Optionally, display an error message to the user
  } finally {
    loading.value = false;
  }
};

watch(() => props.modelValue, (newVal) => {
  dialog.value = newVal;
  if (newVal) {
    fetchChats(); // Fetch chats when dialog opens
  }
});

watch(dialog, (newVal) => {
  emit('update:modelValue', newVal);
});

onMounted(() => {
  // Initial fetch if dialog is somehow open on mount (unlikely with v-model)
  if (dialog.value) {
    fetchChats();
  }
});
</script>
