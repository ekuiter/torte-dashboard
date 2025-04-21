<template>
  <v-app-bar class="px-3" flat>
    <v-spacer>

    </v-spacer>

    <v-icon class="cursor-pointer" size="x-large" @click.native.stop="toggleTheme"
      v-if="theme.global.current.value.dark == false" icon="mdi-cake"></v-icon>
    <img class="cursor-pointer" v-else src="public/dimcake.svg" @click.native.stop="toggleTheme"></img>
    <v-btn @click="reset" rounded size="x-large">
      <h1>
        Torte Dashboard
      </h1>
    </v-btn>
    <v-spacer>
    </v-spacer>
  </v-app-bar>

  <v-container>
    <v-responsive>
      <v-row>
        <v-col md="6">

          <v-autocomplete variant="solo-filled" class=" ma-2" v-model="selectedProject"
            v-on:update:model-value="getPlot" label="Select Project" :items="projects">

          </v-autocomplete>
        </v-col>
        <v-col md="6">
          <v-autocomplete variant="solo-filled" class=" ma-2" v-model="selectedPlot" v-on:update:model-value="getPlot"
            label="Select Plot" :items="plotsForProject" item-title="displayName" item-value="idName">

          </v-autocomplete>
        </v-col>
      </v-row>
      <box-plot v-if="showBoxPlot()" :plot-path="plotPath" :plot-data="currentPlotData">
      </box-plot>
      <scatter-plot v-else-if="showScatterPlot()" :plot-path="plotPath" :plot-data="currentPlotData"
        :current-value="getCurrentScatterData()" :history-data="getHistory()"></scatter-plot>
      <!-- <v-card v-html="mainPageDescription"></v-card> -->
      <!-- <v-sheet :elevation="13" border rounded> -->
        <ContentRenderer v-if="mainPageDescription && !(selectedPlot && selectedProject)" :value="mainPageDescription" />
      <!-- </v-sheet> -->
    </v-responsive>
  </v-container>
</template>
<script lang="ts" setup>
import { ref, type Ref } from 'vue';
import data from "public/init.json"
// import mainPageDescription from "public/mainPageDescription.md"
import type { ScatterData, PlotData } from './interfaces';
const mainPageDescription = await queryCollection('blog').path('/description').first()
const selectedPlot: Ref<string | null> = ref(null);
const currentPlotData: Ref<PlotData | null> = ref(null)
const currentScatterData: Ref<ScatterData | null> = ref(null)
const plotPath: Ref<string | null> = ref(null);
const projects: Ref<string[]> = ref(Object.keys(data.projectData));
const selectedProject: Ref<string | null> = ref(null);
const plotsForProject: Ref<string[]> = ref(getPlotsForProj());
const plots: Ref<string[]> = ref(Object.keys(data.plotData));


import { useTheme } from 'vuetify'

const theme = useTheme()

function toggleTheme() {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
}


function showBoxPlot() {
  console.log(selectedPlot.value)
  return selectedPlot.value != null && data.plotData[selectedPlot.value].plotType == 'box'
}
function showScatterPlot() {
  return selectedPlot.value != null && data.plotData[selectedPlot.value].plotType == 'scatter'
}

function getHistory() {
  console.log("history:", currentScatterData.value)
  return currentScatterData.value?.history
}
function getCurrentScatterData() {
  console.log("currentscatter: ", currentScatterData.value?.currentValue);
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
async function init() {
  reset()
  projects.value = Object.keys(data.projectData)
  plots.value = Object.keys(data.plotData)
  console.log("in init: ", projects.value)
  mainPageDescription.value = data.mainPageDescription
  console.log(mainPageDescription.value)
}

function containsString(): boolean {
  return plotsForProject.value.some(obj =>
    obj.idName == selectedPlot
  );
}

function reset() {
  selectedPlot.value = null
  selectedProject.value = null
  currentPlotData.value = null
  currentScatterData.value = null
  plotPath.value = null
  plotsForProject.value = []
  window.location.hash = ""
}
function isValidConfig(): boolean {
  if (selectedPlot.value != null && selectedProject.value != null) {
    console.log("here")
    if (selectedPlot.value! in data.projectData) {
      selectedProject.value = Object.keys(data.projectData)[0]
    }
    console.log("here2", selectedProject.value)
    if (selectedPlot.value in data.projectData[selectedProject.value]) {
      return true
    }
    selectedPlot.value = Object.keys(data.projectData[selectedProject.value])[0]
    console.log("here3", selectedPlot.value)
    return false
  }
  else {
    return true
  }
}
function getPlot() {
  console.log(selectedPlot.value)
  isValidConfig()
  getPlotsForProj()
  console.log(selectedPlot.value, selectedProject.value, plotsForProject.value)
  if (!containsString) {
    return
  }
  if (selectedPlot.value != null && selectedProject.value != null) {
    window.location.hash = `/${selectedProject.value}~${selectedPlot.value}`
    currentScatterData.value = {
      currentValue: data.projectData[selectedProject.value][selectedPlot.value].currentValue,
      history: data.projectData[selectedProject.value][selectedPlot.value].history,

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
  init()
  if (window.location.hash === "") {
    console.log("no hash")
  }
  else {
    if (window.location.hash.replace("#/", "").split("~").length ==0 ){
      reset()
    } 
    selectedProject.value = window.location.hash.replace("#/", "").split("~")[0] ?? null
    if (selectedProject.value === "") {
      selectedPlot.value = null
    }
    selectedPlot.value = window.location.hash.replace("#/", "").split("~")[1] ?? null
    console.log("start: ", selectedProject.value, selectedPlot.value)
    if (!isValidConfig()) {
      alert("given configuration was invalid. Reverted to default.")
    }
    getPlot()
  }
}
</script>