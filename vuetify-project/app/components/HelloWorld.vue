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
  <v-container class="fill-height pa-2">
    <v-responsive class="align-centerfill-height mx-auto" max-width="1300">
      <div class="text-center">
        <v-icon class="mb-4" size="150" icon="mdi-cake" />

        <h1 class="text-h2 font-weight-bold">Torte Dashboard</h1>
      </div>

      <div class="py-4"></div>
      <v-row>
        <v-select v-model="selectedProject" v-on:update:model-value="getPlot" label="Select Project"
          :items="projects"></v-select>
        <v-select v-model="selectedPlot" v-on:update:model-value="getPlot" label="Select Plot"
          :items="plotsForProject"></v-select>
      </v-row>
      <v-card v-show="plotPath != null">
        <h2 id="iframeHeader"></h2>
        <div id="iframe-container">
          <iframe align="center" title="Plot" id="plot" :src="plotPath"
            style="height:800px;width:1510px;border:none;display:block"></iframe>
        </div>
      </v-card>
    </v-responsive>
  </v-container>
</template>
<script lang="ts" setup>
import { ref, type Ref, onMounted } from 'vue';
import data from "public/init.json"
console.log(data)
const plotPath: Ref<string | null> = ref(null);
const projects: Ref<string[]> = ref(Object.keys(data.projectData));
const selectedPlot: Ref<string | null> = ref(null);
const selectedProject: Ref<string | null> = ref(null);
const plotsForProject: Ref<string[]> = ref(getPlotsForProj());
const plots: Ref<string[]> = ref(Object.keys(data.plotData));
// let keys = [];
// let titleProj = document.getElementById("iframeHeader");
// let s = document.getElementById("dataSelector");
// let plotDesc = document.getElementById("plotDesc")
// let lastWeekP = document.getElementById("lastWeek")
// let cmpLastRev = document.getElementById("cmpLastRevision")
let currentValueP = document.getElementById("currentValue")
// function updateProject(p: string) {
//   selectedProject.value = p
// }
// function updatePlot(p: string) {
//   selectedPlot.value = p
// }

function getPlotsForProj() {
  if (selectedProject.value == null) {
    return []
  }
  plotsForProject.value = Object.keys(data.projectData[selectedProject.value])
}
function init() {
  projects.value = Object.keys(data.projectData)
  plots.value = Object.keys(data.plotData)
  console.log("in init: ", projects.value)
  // for (const proj of projects) {
  //   if (i == 0) {
  //     selectedProj = proj;
  //     let j = 0;
  //     let setDef = false;
  //     for (const plot of plots) {
  //       console.log(plot)
  //       var o = document.createElement('option');
  //       o.id = plot
  //       o.value = `option${j}`
  //       o.title = data.plotData[plot]["title"]
  //       o.innerText = data.plotData[plot]["title"]
  //       if (plot in data.projectData[proj]) {
  //         o.hidden = false
  //         if (setDef == false) {
  //           selectedPlot = o.id
  //           titleProj.innerText = `Selected: ${selectedPlot} for ${proj} (Default)`
  //           o.selected = true;
  //           setDef = true;
  //         }
  //       }
  //       else {
  //         o.classList.add("linuxOnly")
  //         o.hidden = true;
  //       }
  //       j++;
  //       s.appendChild(o);
  //     }
  //   }
  //   var o = document.createElement('li');
  //   o.id = proj
  //   o.addEventListener("click", function () {
  //     document.getElementById("side-menu").classList.remove("active");
  //     titleProj.innerText = `Selected ${selectedPlot} for ${proj}`
  //     selectedProj = proj;
  //     let updated = false;
  //     Array.from(s.options).forEach(function (option_element) {
  //       if (!(selectedPlot in allData.projectData[selectedProj])) {
  //         if (!updated && option_element.id in allData.projectData[selectedProj]) {
  //           option_element.selected = true
  //           updated = true;
  //           selectedPlot = option_element.id
  //         }
  //       }
  //       if (option_element.id in allData.projectData[selectedProj]) {
  //         option_element.hidden = false;
  //       }
  //       else {
  //         option_element.hidden = true;
  //       }
  //     });
  //     getPlot()
  //   })
  //   o.innerText = proj
  //   m.appendChild(o);
  //   i++
  // }
}

function getPlot() {
  getPlotsForProj()
  if (plotsForProject.value.indexOf(selectedPlot.value) == -1) {
    return
  }
  console.log("in getplot: ", selectedPlot.value, selectedProject.value)
  if (selectedPlot.value != null && selectedProject.value != null) {
    const path = `figures/${selectedPlot.value}/${selectedPlot.value}-${selectedProject.value.replace("/", "-")}.html`
    plotPath.value = path
  }  // titleProj.innerText = `Selected ${allData.plotData[selectedPlot]["title"]} for ${selectedProj}`
  // document.getElementById("plot").src = path
  // plotDesc.innerText = allData.plotData[selectedPlot]["desc"]
  // currentValueP.innerText = allData.projectData[selectedProj][selectedPlot].currentValue ?? "n.A."
  // lastWeekP.innerText = allData.projectData[selectedProj][selectedPlot].cmpLastWeek ?? "n.A."
  // cmpLastRev.innerText = allData.projectData[selectedProj][selectedPlot].cmpLastRevision ?? "n.A."
}
if (!import.meta.env.SSR) {
  window.addEventListener('load', () => { init });
}
</script>