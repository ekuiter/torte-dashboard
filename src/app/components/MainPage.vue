<template>
  <v-app-bar class="px-3" flat>
    <v-spacer>

    </v-spacer>

    <v-icon class="cursor-pointer" size="x-large" @click.native.stop="toggleTheme"
      v-if="theme.global.current.value.dark == false" icon="mdi-cake"></v-icon>
    <img style="width:32px;height: 32px" class="cursor-pointer" v-else src="public/dimcake.svg"
      @click.native.stop="toggleTheme"></img>
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
            v-on:update:model-value="getPlot" label="Select Project" :items="sortProjects()">
          </v-autocomplete>
        </v-col>
        <v-col md="6">
          <v-autocomplete variant="solo-filled" class=" ma-2" v-model="selectedPlot" v-on:update:model-value="getPlot"
            label="Select Plot" :items="sortPlots()" item-title="displayName" item-value="idName">
          </v-autocomplete>
        </v-col>
      </v-row>
      <box-plot v-if="!notFound && showBoxPlot()" :plot-path="plotPath" :plot-data="currentPlotData">
      </box-plot>
      <scatter-plot
        v-else-if="!notFound && selectedProject && showScatterPlot() && Object.keys(currentScatterData?.currentValue).length != 0"
        :plot-path="plotPath" :plot-data="currentPlotData" :current-value="getCurrentScatterData()"
        :history-data="getHistory()"></scatter-plot>
      <not-found-info-box v-else-if="notFound || (selectedProject != null && selectedPlot != null)"
        :plot-data="currentPlotData" :project="selectedProject"></not-found-info-box>
      <ContentRenderer v-if="mainPageDescription && !(selectedPlot && selectedProject)" :value="mainPageDescription" />
    </v-responsive>
  </v-container>
</template>
<script lang="ts" setup>
import { ref, type Ref } from 'vue';
import data from "public/init.json"
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
const notFound = ref(false);
const notFoundPlot = ref("")
import { useTheme } from 'vuetify'
import type { RefSymbol } from '@vue/reactivity';

const theme = useTheme()

function toggleTheme() {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
}

function sortPlots() {
  return Array.from(plotsForProject.value).toSorted()
}

function sortProjects() {
  return Array.from(projects.value).toSorted()
}
function showBoxPlot() {
  return selectedPlot.value != null && data.plotData[selectedPlot.value].plotType == 'box'
}
function showScatterPlot() {
  return selectedPlot.value != null && data.plotData[selectedPlot.value].plotType == 'scatter'
}

function getHistory() {
  return currentScatterData.value?.history
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
  console.log("plotsForProject.value")
  console.log(plotsForProject.value)

}
async function init() {
  notFound.value = false
  projects.value = Object.keys(data.projectData)
  plots.value = Object.keys(data.plotData)
  mainPageDescription.value = data.mainPageDescription
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
    if (selectedPlot.value! in data.projectData) {
      selectedProject.value = Object.keys(data.projectData)[0]
    }
    if (selectedPlot.value in data.projectData[selectedProject.value]) {
      return true
    }
    selectedPlot.value = Object.keys(data.projectData[selectedProject.value])[0]
    return false
  }
  else {
    return true
  }
}
function getPlot() {
  notFound.value = false;
  console.log(selectedPlot.value)
  if (selectedPlot.value  && data.plotData[selectedPlot.value]["plotType"] == "scatter" &&  Object.keys(data.projectData[selectedProject.value][selectedPlot.value]).length == 0) {
    console.log("not found")
    notFoundPlot.value = data.plotData[selectedPlot.value]["displayName"]
    notFound.value = true;
    return
  }
  isValidConfig()

  getPlotsForProj()
  if (!containsString) {
    return
  }
  if (selectedPlot.value != null && selectedProject.value != null) {
    window.location.hash = `/${selectedProject.value}~${selectedPlot.value}`
    currentScatterData.value = {
      currentValue: data.projectData[selectedProject.value][selectedPlot.value].currentValue,
      history: data.projectData[selectedProject.value][selectedPlot.value].history,

    }
    currentPlotData.value = data.plotData[selectedPlot.value]
    const path = `figures/${selectedPlot.value}/${selectedPlot.value}-${selectedProject.value.replace("/", "-")}.html`
    plotPath.value = path
  }
}
if (!import.meta.env.SSR) {
  window.addEventListener('load', () => { init });
  init()
  if (window.location.hash !== "") {
    if (window.location.hash.replace("#/", "").split("~").length == 0) {
      reset()
    }
    selectedProject.value = window.location.hash.replace("#/", "").split("~")[0] ?? null
    if (selectedProject.value === "") {
      selectedPlot.value = null
    }
    selectedPlot.value = window.location.hash.replace("#/", "").split("~")[1] ?? null
    if (!isValidConfig()) {
      alert("given configuration was invalid. Reverted to default.")
    }
    getPlot()
  }
}
</script>