<template>
    <v-container>
        <v-row>
            <v-col cols="12" :xl="12" :lg="12" :md="12" sm="12" xs="12" :order="plotColOrder">
                <v-card class="overflow-y-auto" max-height="50vh" v-scroll.self="onScroll">
                    <template v-slot:title>
                        <span class="font-weight-black text-wrap">{{ plotData?.displayName }}</span>
                    </template>

                    <v-card-text class="bg-surface-light pt-4 text-left text-body-2">
                        <div>
                            '{{plotData?.displayName}}' could not be shown for {{ project }}. A possible reason for this is that failures occurred during the extraction, transformation, or analysis of its feature model. 
                            <br>(Compare with Section 6.3.1 of "How Configurable is the Linux Kernel? Analyzing Two Decades of Feature-Model History" - Kuiter et. al, 2025)
                        </div>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>
<script setup lang="ts">
import type { PlotData, ScatterData, ByExtractor, HistoryData } from './interfaces';
import { useDisplay } from 'vuetify'
const props = defineProps<{
    plotData?: PlotData | null,
    project: string | null
}>()
const scrollInvoked = ref(0)
function onScroll() {
    scrollInvoked.value++
}
function getHistoryTitle(name: string) {
    const years = name.split("-")[0]
    if (years == "1") {
        return years + " year ago"
    }
    return years + " years ago"
}
const { name, mobile } = useDisplay()
const plotColOrder = computed(() => {
    console.log(name.value, mobile.value, name.value)

    if (mobile.value == true && name.value !== "md") {
        return 'first'
    }
    switch (name.value) {
        case 'xs': return 'first'
        case 'sm': return 'first'
        case 'md': return "last"
        case 'lg': return 'last'
        case 'xl': return 'last'
        case 'xxl': return 'last'
    }
})
const height = computed(() => {
    // name is reactive and
    // must use .value
    if (mobile.value == true) {
        return 'fill-height'
    }
    switch (name.value) {
        case 'xs': return 'fill-height'
        case 'sm': return '60vh'
        case 'md': return "40vh"
        case 'lg': return '50vh'
        case 'xl': return '60vh'
        case 'xxl': return '60vh'
    }

    return undefined
})
</script>