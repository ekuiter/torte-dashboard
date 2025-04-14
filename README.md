# torte-dashboard
Semi-Static web interface for visualization of pre-executed [torte](https://github.com/ekuiter/torte) simulations.

## 1. Usage

### Generate Data

Open `gen_initJson.ipybn`. At the top, you will find a cell labeled `CONFIG VARIABLES`. These specify various paths in the program. 

1. `linux_output_directory`: The directory in which the torte experiment results are located.
2. `nonlinux_configpath`: The path to the configuration file from which the non-linux data will be generated and merged into `init.json`. 

The latter points to a json file that follows this structure: 

```
{
    "PROJECT": {
        "output_directory": "path/to/experiment_dir",
        "ignore_systems": [
            "SUBSYSTEM-1",
            "SUBSYSTEM-N",
            "this list can also be empty"
        ],
    },
    // for instance
    "axtls": {
        "output_directory": "output",
        "ignore_systems": [
            "uclibc-ng",
            "embtoolkit"
        ]
    },
}
```
Populate this file according to your available experiment results.
The config file also includes a list to filter out/ignore certain systems inside a given project. For `axtls`, we are ignoring `uclibc-ng` and `embtoolkit`. Modify this filter according to your needs. Be aware, that no filtering in a mixed dataset may result in skewed data calculation.

Next, inside the `vuetify-project/public/init.json`, under the `projectData` key, you can add more projects. 
For a successful extraction of data from your experiment results, there are three things to consider:

1. It is important that the keys match with the respective one inside `plotData`.
2. We do not recommend modifying the `idName` and `plotType` values as this will break the frontend. Values under `displayName` and `description` are not processed in a way that a modification would break anything. 

Lastly, the bottom two cells of `gen_initJson.ipynb` need to be executed to process the experiment data, and extend the `init.json` file. Naturally, you may want to comment out, or simply not execute, the linux cell if you dont have the linux experiment data.

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
Specifically, we open a development server by calling `npm run dev` from within `vuetify-project` and `npm run generate` for SSG.
After the project has been built, we can open a local server using `npx serve .output/public` or even move the `public` folder into a `<userName>.github.io` repository. 