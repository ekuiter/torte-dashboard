<template>
    <v-card class="overflow-y-auto" max-height="50vh" v-scroll.self="onScroll">
        <template v-slot:title>
            <span class="font-weight-black text-wrap">{{ title }}</span>
        </template>

        <v-card-text class="bg-surface-light pt-4 text-center text-body-2">
            <span >
                {{ value }} 
            </span>
            <v-spacer></v-spacer>
            <span>
                {{ date }}
            </span>
        </v-card-text>
    </v-card>
</template>
<script setup lang="ts">
const scrollInvoked = ref(0)
function onScroll() {
    scrollInvoked.value++
}
defineProps<{
    title?: string | null,
    value?: string | null,
    date?: string | null,
}>()

</script>