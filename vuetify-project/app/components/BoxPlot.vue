<template>
    <v-container>
        <v-row>
            <v-col cols="12" lg="12">
                <v-card class="overflow-y-auto" v-scroll.self="onScroll">
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
        </v-row>
        <v-row>
            <v-col cols="12" lg="12">
                <v-sheet rounded="lg">
                    <v-card :v-else-if="plotPath != null">
                        <h2 id="iframeHeader"></h2>
                        <div id="iframe-container">
                            <iframe align="center" title="Plot" id="plot" :src="plotPath"
                                style="height:800px;width:1510px;border:none;display:block"></iframe>
                        </div>
                    </v-card>
                </v-sheet>
            </v-col>
        </v-row>
    </v-container>
</template>
<script setup lang="ts">
import type { PlotData } from './interfaces';


defineProps<{
    plotPath?: string | null,
    plotData?: PlotData | null,
}>()

const scrollInvoked = ref(0)
function onScroll() {
    scrollInvoked.value++
}

</script>