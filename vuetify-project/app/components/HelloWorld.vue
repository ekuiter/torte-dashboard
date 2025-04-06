<style>
#iframe-container {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}
</style>
<template>
  <v-app-bar class="px-3" flat>
    <v-spacer>

    </v-spacer>

    <h1>
      <v-icon icon="mdi-cake" />
      Torte Dashboard
    </h1>
    <v-spacer>
    </v-spacer>
  </v-app-bar>

  <v-container>
    <v-responsive class="mx-auto" max-width="1300">
      <v-row>
        <v-select variant="solo-filled" class=" ma-2" v-model="selectedProject" v-on:update:model-value="getPlot"
          label="Select Project" :items="projects"></v-select>
        <!-- <v-spacer></v-spacer> -->
        <v-select variant="solo-filled" class=" ma-2" v-model="selectedPlot" v-on:update:model-value="getPlot"
          label="Select Plot" :items="plotsForProject" item-title="displayName" item-value="idName"></v-select>
      </v-row>
      <box-plot v-if="showBoxPlot()" :plot-path="plotPath" :plot-data="currentPlotData">
      </box-plot>
      <scatter-plot v-else-if="showScatterPlot()" :plot-path="plotPath" :plot-data="currentPlotData"
        :current-value="getCurrentScatterData()"></scatter-plot>
    </v-responsive>
  </v-container>
</template>
<script lang="ts" setup>
import { ref, type Ref } from 'vue';
import type { PlotData, ScatterData } from './interfaces';
const selectedPlot: Ref<string | null> = ref(null);
import data from "public/init.json"
import { leafSelectStrategy } from 'vuetify/lib/composables/nested/selectStrategies.mjs';
const currentPlotData: Ref<PlotData | null> = ref(null)
const currentScatterData: Ref<ScatterData | null> = ref(null)
const plotPath: Ref<string | null> = ref(null);
const projects: Ref<string[]> = ref(Object.keys(data.projectData));
const selectedProject: Ref<string | null> = ref(null);
const plotsForProject: Ref<string[]> = ref(getPlotsForProj());
const plots: Ref<string[]> = ref(Object.keys(data.plotData));
function showBoxPlot() {
  console.log(selectedPlot.value)
  return selectedPlot.value != null && data.plotData[selectedPlot.value].plotType == 'box'
}
function showScatterPlot() {
  return selectedPlot.value != null  && data.plotData[selectedPlot.value].plotType == 'scatter'
}
function getCurrentScatterData() {
  return currentScatterData.value?.currentValue
}
function getPlotsForProj() {
  if (selectedProject.value == null) {
    return []
  }
  plotsForProject.value = []
  for (let plot of Object.keys(data.projectData[selectedProject.value])) {
    plotsForProject.value = [...plotsForProject.value, data.plotData[plot]]
  }
}
function init() {
  projects.value = Object.keys(data.projectData)
  plots.value = Object.keys(data.plotData)
  console.log("in init: ", projects.value)
}

function containsString(): boolean {
  return plotsForProject.value.some(obj =>
    obj.idName == selectedPlot
  );
}

function getPlot() {
  console.log(selectedPlot.value)
  getPlotsForProj()
  console.log(selectedPlot.value, selectedProject.value, plotsForProject.value)
  if (!containsString) {
    return
  }
  if (selectedPlot.value != null && selectedProject.value != null) {
    currentScatterData.value = {
      currentValue: data.projectData[selectedProject.value][selectedPlot.value].currentValue
    }
    console.log(currentScatterData)
    console.log(currentScatterData.value)
    currentPlotData.value = data.plotData[selectedPlot.value]
    const path = `figures/${selectedPlot.value}/${selectedPlot.value}-${selectedProject.value.replace("/", "-")}.html`
    console.log(path)
    plotPath.value = path
  }
}
if (!import.meta.env.SSR) {
  window.addEventListener('load', () => { init });
}
</script>