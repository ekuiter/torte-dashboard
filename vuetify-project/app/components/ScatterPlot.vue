<template>
    <v-container>
        <v-row>
            <v-col>

                <info-card :title="plotData?.displayName" :value="plotData?.description" :textAlign="'text-left'">
                </info-card>
            </v-col>
        </v-row>
        <v-row>
            <v-col v-if="currentValue != null">
                <info-card v-if="typeof currentValue[Object.keys(currentValue)[0]] === 'string'" title="Current Value" :value="currentValue.value" :date="currentValue.date">
                </info-card>
                <info-card v-else-if="currentValue != null"
                    v-for="item in Object.entries(currentValue)" :key="item" :title="`Current Value&#13;(${item[0]})`"
                    :value="item[1].value" :date="item[1].date">
                </info-card>

            </v-col>

            <v-col>
                <v-sheet rounded="lg">
                    <v-card :v-else-if="plotPath != null">
                        <h2 id="iframeHeader"></h2>
                        <div id="iframe-container">
                            <iframe align="center" title="Plot" id="plot" :src="plotPath"
                                style="height:60vh;width:60vw;border:none;display:block"></iframe>
                        </div>
                    </v-card>
                </v-sheet>
            </v-col>
        </v-row>
    </v-container>
</template>
<script setup lang="ts">
import type { PlotData, ScatterData, ByExtractor } from './interfaces';

const props = defineProps<{
    plotPath?: string | null,
    plotData?: PlotData | null,
    currentValue?: ByExtractor | Scatterdata | null
}>()

const scrollInvoked = ref(0)
function onScroll() {
    scrollInvoked.value++
}

</script>