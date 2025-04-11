<template>
    <v-container>
        <v-row>
            <v-col>
                <info-card :title="plotData?.displayName" :value="plotData?.description" :textAlign="'text-left'">
                </info-card>
            </v-col>
            <v-col>
                <v-sheet :height="height" :width="width">
                    <iframe :v-if="plotPath != null" align="center" title="Plot" id="plot" :src="plotPath!"
                        style="height:100%;width:100%;border:none;display:block"></iframe>
                </v-sheet>
            </v-col>
        </v-row>
    </v-container>
</template>
<script setup lang="ts">
import type { PlotData } from './interfaces';
import { useDisplay } from 'vuetify'


defineProps<{
    plotPath?: string | null,
    plotData?: PlotData | null,
}>()

const scrollInvoked = ref(0)
function onScroll() {
    scrollInvoked.value++
}
const { name, mobile } = useDisplay()
const width = computed(() => {
    // name is reactive and
    // must use .value
    if (mobile.value == true) {
        return '90vw'
    }
    switch (name.value) {
        case 'xs': return '60vw'
        case 'sm': return '60vw'
        case 'md': return '60vw'
        case 'lg': return '60vw'
        case 'xl': return '60vw'
        case 'xxl': return '60vw'
    }

    return undefined
})
const height = computed(() => {
    // name is reactive and
    // must use .value
    if (mobile.value == true) {
        return '90vh'
    }
    switch (name.value) {
        case 'xs': return '60vh'
        case 'sm': return '60vh'
        case 'md': return '60vh'
        case 'lg': return '60vh'
        case 'xl': return '60vh'
        case 'xxl': return '60vh'
    }

    return undefined
})
</script>