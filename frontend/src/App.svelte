<script>
  import {
    colorScheme,
    SvelteUIProvider,
    Button,
    ActionIcon,
    Group,
  } from "@svelteuidev/core";
  import Main from "./Main.svelte";
  import { onMount } from "svelte";
  let projects = [];
  let plotOptions;
  let open = false;
  let selectedProject = null;
  function toggleSidebar() {
    if (document.getElementById("mySidenav") == null) {
      open = false;
      return;
    }
    if (open) {
      document.getElementById("mySidenav").style.width = "0";
      open = false;
    } else {
      document.getElementById("mySidenav").style.width = "250px";
      open = true;
    }
  }
  onMount(async () => {
    try {
      colorScheme.update(() => "dark");
      const response = await fetch("/init");
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const data = await response.json();
      projects = data["projects"];
      plotOptions = data["plots"];
      console.log(Object.keys(plotOptions));
      console.log(Object.entries(plotOptions));
      console.log(Object.values(plotOptions));
    } catch (err) {
      console.log(err);
      error = err;
      loading = false;
    }
  });
</script>

<SvelteUIProvider withGlobalStyles themeObserver={colorScheme}>
  <Group>
    <ActionIcon style="margin:0;" on:click={toggleSidebar}>
      <img src="svgs/hamburger.svg" alt="My Happy SVG" />
    </ActionIcon>
    <h1>Torte Dashboard</h1>

  </Group>
  <div id="mySidenav" class="sidenav">
    <ActionIcon on:click={toggleSidebar}>
      <img src="svgs/close.svg" alt="My Happy SVG" />
    </ActionIcon>
    {#each projects as item}
      <Button
        style="width: 90%;margin:auto;margin-bottom: 5px"
        variant="default"
        ripple
        on:click={() => {
          selectedProject = item;
          toggleSidebar()}}
      >
        {item}
      </Button>
    {/each}
  </div>
  <Main plotOptions={plotOptions} selectedProject={selectedProject}/>
  
</SvelteUIProvider>

<style>
  .sidenav {
    height: 100%;
    width: 0;
    position: fixed;
    z-index: 1;
    top: 0;
    left: 0;
    background-color: #111;
    overflow-x: hidden;
    transition: 0.5s;
    padding-top: 10px;
  }

  @media screen and (max-height: 300px) {
    .sidenav {
      padding-top: 15px;
    }
  }
</style>
