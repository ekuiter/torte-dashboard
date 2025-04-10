<template>
    <v-card class=" ma-2" min-height="10vh">
        <template v-slot:title>
            <span class="font-weight-black text-wrap">Current Value <br>(KConfigReader)</span>
        </template>

        <v-card-text class="bg-surface-light pt-4" v-text="currentValue?.KConfig">
        </v-card-text>
    </v-card>
    <v-card class=" ma-2" min-height="10vh">
        <template v-slot:title>
            <span class="font-weight-black text-wrap">Current Value <br>(KClause)</span>
        </template>

        <v-card-text class="bg-surface-light pt-4" v-text="currentValue?.KClause">
        </v-card-text>
    </v-card>
</template>
<script setup lang="ts">
import type { ByExtractor } from './interfaces';

defineProps<{
    currentValue?: ByExtractor,
}>()

</script>