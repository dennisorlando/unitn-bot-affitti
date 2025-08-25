<template>
  <v-container fluid class="rental-listings-container">
    <!-- Header Section -->
    <v-row class="mb-4">
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center">
          <div>
            <h2 class="text-h4 font-weight-bold text-primary">
              Available Rentals
            </h2>
            <p class="text-subtitle-1 text-medium-emphasis">
              {{ filteredRentals.length }} properties found
            </p>
          </div>

          <!-- Search and Filter Controls -->
          <div class="d-flex gap-3">
            <v-text-field
                v-model="searchQuery"
                prepend-inner-icon="mdi-magnify"
                label="Search location..."
                variant="outlined"
                density="compact"
                style="min-width: 250px;"
                clearable
            />

            <v-select
                v-model="selectedRoomType"
                :items="roomTypeOptions"
                label="Room Type"
                variant="outlined"
                density="compact"
                style="min-width: 150px;"
                clearable
            />

            <v-select
                v-model="selectedGender"
                :items="genderOptions"
                label="Gender"
                variant="outlined"
                density="compact"
                style="min-width: 130px;"
                clearable
            />

            <v-range-slider
              v-model="selectedPriceRange"
              :max="maxPrice"
              :min="0"
              step="50"
              label="Price Range"
              class="align-center"
              style="min-width: 200px;"
              thumb-label="always"
            >
              <template v-slot:prepend>
                <span class="text-body-2 font-weight-medium">€{{ selectedPriceRange[0] }}</span>
              </template>
              <template v-slot:append>
                <span class="text-body-2 font-weight-medium">€{{ selectedPriceRange[1] }}</span>
              </template>
            </v-range-slider>

            <v-select
              v-model="sortBy"
              :items="sortOptions"
              item-text="title"
              item-value="value"
              label="Sort by"
              variant="outlined"
              density="compact"
              style="min-width: 180px;"
            />
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Rental Cards Grid -->
    <v-row>
      <v-col
          v-for="rental in paginatedRentals"
          :key="rental.id"
          cols="12"
          md="6"
          lg="4"
          xl="3"
      >
        <v-card
            class="rental-card"
            elevation="2"
            hover
            :ripple="false"
        >
          <!-- Price Header -->
          <v-card-title class="bg-primary text-white d-flex justify-space-between align-center pa-3">
            <div>
              <span class="text-h5 font-weight-bold">
                €{{ rental.price_per_month || 'N/A' }}
              </span>
              <span class="text-body-2 ml-1">/month</span>
            </div>
            <v-chip
                :color="getRoomTypeColor(rental.room_type)"
                variant="elevated"
                size="small"
            >
              {{ formatRoomType(rental.room_type) }}
            </v-chip>
          </v-card-title>

          <!-- Location and Availability -->
          <v-card-subtitle class="pa-3 pb-2">
            <div class="d-flex align-center mb-2">
              <v-icon size="small" class="me-2">mdi-map-marker</v-icon>
              <span class="text-body-2">
                {{ rental.location || 'Location not specified' }}
              </span>
            </div>
            <div class="d-flex align-center" v-if="rental.available_from">
              <v-icon size="small" class="me-2">mdi-calendar</v-icon>
              <span class="text-body-2">
                Available from {{ rental.available_from }}
              </span>
            </div>
          </v-card-subtitle>

          <!-- Main Content -->
          <v-card-text class="pa-3">
            <!-- Target Audience & Gender -->
            <div class="mb-3">
              <div class="d-flex gap-2 mb-2">
                <v-chip
                    v-if="rental.target_audience"
                    size="x-small"
                    color="blue-grey"
                    variant="tonal"
                >
                  {{ formatTargetAudience(rental.target_audience) }}
                </v-chip>
                <v-chip
                    v-if="rental.target_gender && rental.target_gender !== 'any'"
                    size="x-small"
                    :color="rental.target_gender === 'female' ? 'pink' : 'blue'"
                    variant="tonal"
                >
                  {{ formatGender(rental.target_gender) }}
                </v-chip>
              </div>
            </div>

            <!-- Utilities -->
            <div class="mb-3" v-if="rental.utilities_included !== null">
              <v-chip
                  :color="rental.utilities_included ? 'green' : 'orange'"
                  variant="tonal"
                  size="small"
              >
                <v-icon start>
                  {{ rental.utilities_included ? 'mdi-check-circle' : 'mdi-alert-circle' }}
                </v-icon>
                {{ rental.utilities_included ? 'Utilities Included' : 'Utilities Extra' }}
              </v-chip>
            </div>

            <!-- Contract Duration -->
            <div class="mb-3" v-if="rental.contract_duration">
              <div class="d-flex align-center">
                <v-icon size="small" class="me-2">mdi-file-document</v-icon>
                <span class="text-body-2">{{ rental.contract_duration }}</span>
              </div>
            </div>

            <!-- Amenities -->
            <div v-if="rental.amenities && rental.amenities.length > 0">
              <p class="text-body-2 font-weight-medium mb-2">Amenities:</p>
              <div class="d-flex flex-wrap gap-1">
                <v-chip
                    v-for="amenity in rental.amenities.slice(0, 4)"
                    :key="amenity"
                    size="x-small"
                    color="grey"
                    variant="outlined"
                >
                  <v-icon start size="x-small">{{ getAmenityIcon(amenity) }}</v-icon>
                  {{ formatAmenity(amenity) }}
                </v-chip>
                <v-chip
                    v-if="rental.amenities.length > 4"
                    size="x-small"
                    color="grey"
                    variant="text"
                >
                  +{{ rental.amenities.length - 4 }} more
                </v-chip>
              </div>
            </div>

            <!-- Other Features -->
            <div v-if="rental.other && rental.other.length > 0" class="mt-3">
              <p class="text-body-2 font-weight-medium mb-2">Additional Info:</p>
              <div class="d-flex flex-wrap gap-1">
                <v-chip
                    v-for="(feature, index) in rental.other.slice(0, 2)"
                    :key="index"
                    size="x-small"
                    color="indigo"
                    variant="tonal"
                >
                  {{ feature }}
                </v-chip>
                <v-tooltip v-if="rental.other.length > 2" bottom>
                  <template v-slot:activator="{ props }">
                    <v-chip
                        v-bind="props"
                        size="x-small"
                        color="indigo"
                        variant="text"
                    >
                      +{{ rental.other.length - 2 }} more
                    </v-chip>
                  </template>
                  <span>{{ rental.other.slice(2).join(', ') }}</span>
                </v-tooltip>
              </div>
            </div>
          </v-card-text>

          <!-- Actions -->
          <v-card-actions class="pa-3 pt-0">
            <v-spacer />
            <v-btn
                color="primary"
                variant="elevated"
                size="small"
                @click="viewDetails(rental)"
            >
              View Details
            </v-btn>
            <v-btn
                color="success"
                variant="outlined"
                size="small"
                @click="contactOwner(rental)"
            >
              Contact
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- No Results State -->
    <v-row v-if="filteredRentals.length === 0">
      <v-col cols="12" class="text-center py-8">
        <v-icon size="64" color="grey-lighten-1">mdi-home-search</v-icon>
        <h3 class="text-h6 text-grey-darken-1 mt-4">No rentals found</h3>
        <p class="text-body-2 text-grey">Try adjusting your search criteria</p>
      </v-col>
    </v-row>

    <!-- Pagination -->
    <v-row v-if="filteredRentals.length > itemsPerPage" class="mt-4">
      <v-col cols="12" class="d-flex justify-center">
        <v-pagination
            v-model="currentPage"
            :length="totalPages"
            :total-visible="7"
            rounded="circle"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'RentalList',

  data() {
    return {
      rentals: [], // This will be populated from your API
      searchQuery: '',
      selectedRoomType: null,
      selectedGender: null,
      selectedPriceRange: [0, 1000],
      sortBy: 'price-asc',
      sortDesc: false,
      currentPage: 1,
      itemsPerPage: 12,

      roomTypeOptions: [
        { title: 'Single Room', value: 'single' },
        { title: 'Double Room', value: 'double' },
        { title: 'Shared Room', value: 'shared' }
      ],

      genderOptions: [
        { title: 'Any', value: 'any' },
        { title: 'Male Only', value: 'male' },
        { title: 'Female Only', value: 'female' }
      ],
      
      sortOptions: [
        { title: 'Price: Low to High', value: 'price-asc' },
        { title: 'Price: High to Low', value: 'price-desc' }
      ]
    }
  },

  computed: {
    filteredRentals() {
      let filtered = this.rentals;

      // Search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(rental =>
            (rental.location && rental.location.toLowerCase().includes(query))
        );
      }

      // Room type filter
      if (this.selectedRoomType) {
        filtered = filtered.filter(rental => rental.room_type === this.selectedRoomType);
      }

      // Gender filter
      if (this.selectedGender && this.selectedGender !== 'any') {
        filtered = filtered.filter(rental =>
            rental.target_gender === this.selectedGender || rental.target_gender === 'any'
        );
      }

      // Price filter
      filtered = filtered.filter(rental => {
        if (rental.price_per_month === null) return false;
        return rental.price_per_month >= this.selectedPriceRange[0] && rental.price_per_month <= this.selectedPriceRange[1];
      });

      // Sorting
      if (this.sortBy) {
        const [field, order] = this.sortBy.split('-');
        const sortField = field === 'price' ? 'price_per_month' : field;
        filtered.sort((a, b) => {
          const valA = a[sortField];
          const valB = b[sortField];
          if (valA === null) return 1;
          if (valB === null) return -1;
          if (order === 'asc') {
            return valA - valB;
          } else {
            return valB - valA;
          }
        });
      }

      return filtered;
    },

    maxPrice() {
      if (this.rentals.length === 0) return 1000;
      return this.rentals.reduce((max, rental) => {
        return rental.price_per_month > max ? rental.price_per_month : max;
      }, 0);
    },

    totalPages() {
      return Math.ceil(this.filteredRentals.length / this.itemsPerPage);
    },

    paginatedRentals() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredRentals.slice(start, end);
    }
  },

  methods: {
    async fetchRentals() {
      try {
        const response = await fetch('http://localhost:9009/processed_messages');
        this.rentals = await response.json();
      } catch (error) {
        console.error('Error fetching rentals:', error);
      }
    },

    formatRoomType(type) {
      const types = {
        single: 'Single',
        double: 'Double',
        shared: 'Shared'
      };
      return types[type] || 'N/A';
    },

    getRoomTypeColor(type) {
      const colors = {
        single: 'blue',
        double: 'green',
        shared: 'orange'
      };
      return colors[type] || 'grey';
    },

    formatTargetAudience(audience) {
      const audiences = {
        students: 'Students',
        professionals: 'Professionals',
        any: 'Anyone'
      };
      return audiences[audience] || audience;
    },

    formatGender(gender) {
      const genders = {
        male: 'Male Only',
        female: 'Female Only',
        any: 'Any Gender'
      };
      return genders[gender] || gender;
    },

    formatAmenity(amenity) {
      const amenities = {
        wifi: 'WiFi',
        laundry: 'Laundry',
        parking: 'Parking',
        elevator: 'Elevator',
        balcony: 'Balcony',
        kitchen: 'Kitchen'
      };
      return amenities[amenity] || amenity;
    },

    getAmenityIcon(amenity) {
      const icons = {
        wifi: 'mdi-wifi',
        laundry: 'mdi-washing-machine',
        parking: 'mdi-car',
        elevator: 'mdi-elevator',
        balcony: 'mdi-balcony',
        kitchen: 'mdi-chef-hat'
      };
      return icons[amenity] || 'mdi-check';
    },

    viewDetails(rental) {
      // Implement view details functionality
      console.log('Viewing details for rental:', rental.id);
      // You could emit an event or navigate to a detail page
      this.$emit('view-details', rental);
    },

    contactOwner(rental) {
      // Implement contact functionality
      console.log('Contacting owner for rental:', rental.id);
      // You could emit an event or open a contact modal
      this.$emit('contact-owner', rental);
    }
  },

  mounted() {
    this.fetchRentals().then(() => {
      this.selectedPriceRange = [0, this.maxPrice];
    });
  },

  watch: {
    // Reset to first page when filters change
    searchQuery() {
      this.currentPage = 1;
    },
    selectedRoomType() {
      this.currentPage = 1;
    },
    selectedGender() {
      this.currentPage = 1;
    },
    selectedPriceRange() {
      this.currentPage = 1;
    },
    sortBy() {
      this.currentPage = 1;
    }
  }
}
</script>

<style scoped>
.rental-listings-container {
  height: 100%;
  overflow-y: auto;
}

.rental-card {
  transition: transform 0.2s ease-in-out;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.rental-card:hover {
  transform: translateY(-2px);
}

.rental-card .v-card-text {
  flex-grow: 1;
}

.gap-1 > * {
  margin-right: 4px !important;
  margin-bottom: 4px !important;
}

.gap-2 > * {
  margin-right: 8px !important;
  margin-bottom: 4px !important;
}

.gap-3 > * {
  margin-right: 12px !important;
}
</style>