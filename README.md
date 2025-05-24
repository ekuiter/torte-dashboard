# torte-dashboard
Semi-Static web interface for visualization of pre-executed [`TORTE`](https://github.com/ekuiter/torte) simulations.

## 1. Usage

### Writing the Homepage Description

The home page description can be modified in `src/content/description.md`.
Furthermore, the descriptions of the individual metrics can currently be modified inside the `init.json`, specifically under `plotData.*.description`.  
### Generate Figures and Metrics

To generate figures and metrics from TORTE experiment data, tow things are needed:

1. A configuration, found in `gen_init.json`, and
2. the generation script, found in `generation.py` 

The configuration is structured as follows:
```
{
    "nonLinux": {
        "NONLINUX_PROJECT": {
            "output_directory": "output",
            "ignore_systems": [
                "SUBSYSTEM-1",
                "SUBSYSTEM-N"
            ],
            "figures_directory": "src/public/figures"  // the default inside the script, can also be modified or omitted here
        },
        // for instance
        "busybox": {
            "output_directory": "output-busybox",
            "ignore_systems": [
                "busybox-models"
            ],
        }
    },
    "linux": {
        "output_directory": "output-linux",  // Set to null to ignore
        "figures_directory": "src/public/figures"
    }
}
```
Populate this file according to your available experiment results.
The config file also includes a list to filter out/ignore certain systems inside a given project. For `axtls`, we are ignoring `uclibc-ng` and `embtoolkit`. Modify this filter according to your needs. Be aware, that no filtering in a mixed dataset may result in skewed data calculation.

The generated metrics will be saved under the `projectData` key in `src/public/init.json`. 
Under the `plotData` key are meta informations for the metrics, i.e. the plot type or information.
We do not recommend modifying the `idName` and `plotType` values as this will break the frontend. Values under `displayName` and `description` are not processed in a way that a modification would break anything and we encourage you to write descriptions that to your liking.

> In the next section, we report back the iterative process of finding a suitable tech stack. If you are only interested in the current, and final, one - feel free to [skip ahead](#final-teck-stack).

## 2.  Implementation Concept

### First Tech Stack

Our first setup was made up of two things:

1. Astro frontend (used as middleware)
2. expressJS server

The reasoning was quite simple. We do not need an extensively reactive framework like React or Angular, as the frontend will effectively be a visualization tool based on a short selection process. Furthermore, Astro uses a concept called "Island Architecture" which allows for certain elements to be rendered asynchronously. Assuming a call to the server would take a long time, we would rather have a pending animation than an unresponsive site.
Secondly, we decided to use expressJS to build our backend because the choice of server does not matter greatly, and we already have experience using it.

### Complications
While the first iteration of the tech stack would have surely worked, there was room for improvement. 
For instance, the original plots were generated using python code, more specifically the python API of Plotly.
This means that we would either have to call the python scripts from our Javascript backend, or, alternatively, we would have to translate the python scripts into JS.
Because we would like to keep our tech stack as simple as possible, and have no desire to reinvent the wheel, we decided upon a new approach. 

### Second Iteration Tech Stack

The second iteration of our tech stack uses Svelte as our frontend and a Flask server for our backend.
Switching from expressJS allows us to only use python in our backend. However, Astro has no built-in compatibility with python backends.
Therefore, we decided to use svelte instead, because it is easy to use as well as both time and memory efficient as it compiles its components into optimized javascript.

So, the entire workflow will be:
1. user selects what to visualize
2. frontend sends request to server
3. server processes request, calls script
4. script creates figure, export (to file for caching?) as HTML
5. server responds with html 
6. Client renders html 

It is worth noting, that by exporting the figure in html (and not png/jpeg/svg), the user can still interact with the figure in the frontend.

#### ~~Proof of concept~~
~~As of now, this project includes a simple proof of concept.
To start the Flask server, simply run in a terminal:~~

```
// make sure you have flask installed
python server.py  // or flask --app server run
```

### Third Iteration Tech Stack
**TODO**
plain index.html 
downsides, upsides etc

### Final Teck Stack

Motivated by a lack of frontend design skills, we came across a concept called *Static Site Generation* (SSG).

We use `vuetify` (a vueJS extension framework) to effortlessly develop a beautiful frontend and `nuxt` to subsequently generate static html files.
Specifically, we open a development server by calling `npm run dev` from within `src` and `npx nuxt build --preset github_pages` for SSG (in this case, specifically for github pages).
After the project has been built, we can open a local server using `npx serve .output/public` or even move the `public` folder into a `<userName>.github.io` repository. 