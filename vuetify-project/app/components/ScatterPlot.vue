<template>
    <v-container>
        <v-row>
            <v-col v-if="currentValue != null" cols="12" xl="3" lg="3" md="4" sm="12" xs="12">
                <info-card v-if="typeof currentValue[Object.keys(currentValue)[0]] === 'string'" title="Current Value"
                    :value="currentValue.value" :date="currentValue.date">
                </info-card>
                <div class="my-2" v-else-if="currentValue != null" v-for="item in Object.entries(currentValue)"
                    :key="item">
                    <info-card :title="`Current Value&#13;(${item[0]})`" :value="item[1].currentValue.value"
                        :date="item[1].currentValue.date">
                    </info-card>
                    <v-card class="overflow-y-auto my-2" max-height="50vh" v-scroll.self="onScroll">
                        <template v-slot:title>
                            <span class="font-weight-black text-wrap">History: {{ item[0] }}</span>
                        </template>

                        <v-card-text class="bg-surface-light pt-4 text-center text-body-2">
                            <v-table>
                                <tbody>
                                    <tr v-for="history in Object.entries(item[1].history)" :key="item">
                                        <td>{{ getHistoryTitle(history[0]) }}</td>
                                        <td>{{ history[1].value }}</td>

                                    </tr>
                                </tbody>
                            </v-table>
                        </v-card-text>
                    </v-card>
                </div>
                <v-card v-if="historyData != null" class="overflow-y-auto my-2" max-height="50vh"
                    v-scroll.self="onScroll">
                    <template v-slot:title>
                        <span class="font-weight-black text-wrap">History</span>
                    </template>

                    <v-card-text class="bg-surface-light pt-4 text-center text-body-2">
                        <v-table>
                            <tbody>
                                <tr v-for="item in Object.entries(historyData)" :key="item">
                                    <td>{{ getHistoryTitle(item[0]) }}</td>
                                    <td>{{ item[1].value }}</td>
                                </tr>
                            </tbody>
                        </v-table>
                    </v-card-text>
                </v-card>
            </v-col>
            <v-col cols="12" xl="9" lg="9" md="8" sm="12" xs="12">
                <info-card class="my-2" :title="plotData?.displayName" :value="plotData?.description"
                    :textAlign="'text-left'">
                </info-card>
                <v-sheet :height="height" class="my-2">
                    <iframe v-if="plotPath != null" align="center" title="Plot" id="plot" :src="plotPath"
                        style="height:100%; width:100%;border:none;"></iframe>
                </v-sheet>
            </v-col>
        </v-row>
    </v-container>
</template>
<script setup lang="ts">
import type { PlotData, ScatterData, ByExtractor, HistoryData } from './interfaces';
import { useDisplay } from 'vuetify'
const props = defineProps<{
    plotPath?: string | null,
    plotData?: PlotData | null,
    currentValue?: ByExtractor | ScatterData | null,
    historyData?: HistoryData
}>()
const scrollInvoked = ref(0)
console.log("CV: ", props.currentValue)
console.log("HD: ", props.historyData)

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
const width = computed(() => {
    // name is reactive and
    // must use .value
    console.log(name.value)
    if (mobile.value == true) {
        return 'fill-width'
    }
    switch (name.value) {
        case 'xs': return 'fill-width'
        case 'sm': return '60vw'
        case 'md': return 'fill-width'
        case 'lg': return 'fill-width'
        case 'xl': return '60vw'
        case 'xxl': return '60vw'
    }

    return undefined
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
        case 'lg': return 'fill-height'
        case 'xl': return '60vh'
        case 'xxl': return '60vh'
    }

    return undefined
})
console.log(name.value)
</script>