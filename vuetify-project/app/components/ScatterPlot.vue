<template>
    <v-container>
        <v-row>
            <v-col cols="12" lg="2">
                <v-card class="overflow-y-auto" max-height="50vh" v-scroll.self="onScroll">
                    <template v-slot:title>
                        <span class="font-weight-black text-wrap">{{ plotData?.displayName }}</span>
                    </template>

                    <v-card-text class="bg-surface-light pt-4">
                        {{ plotData?.description }}
                        <br>
                        This description field grows automatically
                    </v-card-text>
                </v-card>
            </v-col>

            <v-col cols="12" md="8">
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

            <v-col cols="12" lg="2">

                <v-card class=" ma-2" min-height="10vh" v-scroll.self="onScroll">
                    <template v-slot:title>
                        <span class="font-weight-black text-wrap">Current Value</span>
                    </template>

                    <v-card-text class="bg-surface-light pt-4" v-text="currentValue">
                    </v-card-text>
                </v-card>


            </v-col>
        </v-row>
    </v-container>
</template>
<script setup lang="ts">
import type { PlotData, ScatterData } from './interfaces';

defineProps<{
    plotPath?: string | null,
    plotData?: PlotData | null,
    currentValue?: string | null
}>()

const scrollInvoked = ref(0)
function onScroll() {
    scrollInvoked.value++
}

</script>