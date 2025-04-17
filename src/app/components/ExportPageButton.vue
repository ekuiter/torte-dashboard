<template>
    <div class="pa-4 text-center">
        <v-btn :onclick="test"  prepend-icon="mdi-account-multiple-outline" variant="flat">
            Share
        </v-btn>
    </div>
</template>

<script setup lang="ts">

defineProps<{
    staticPath?: string | null
}>()
function test(){
    navigator.clipboard.writeText("test hallo 123123");
}
</script>