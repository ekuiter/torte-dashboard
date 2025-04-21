
// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  app: {
    baseURL: "/"
  },
  compatibilityDate: '2024-11-01',
  future: {
    compatibilityVersion: 4
  },
  // router: {
  //   options: {
  //     hashMode: true
  //   }
  // },
  devtools: {
    enabled: false,
  },
  ssr: false,
  // hooks: {
  //   'prerender:routes'({ routes }) {
  //     routes.clear() // Do not generate any routes (except the defaults)
  //   }
  // },
  // when enabling ssr option you need to disable inlineStyles and maybe devLogs
  features: {
    inlineStyles: false,
    devLogs: false,
  },

  build: {
    transpile: ['vuetify']
  },

  vite: {
    ssr: {
      noExternal: ['vuetify'],
    },
    assetsInclude: ['**/*.md']
  },

  css: [],
  modules: ['@nuxt/fonts', 'vuetify-nuxt-module', '@nuxt/eslint', '@nuxt/content'],

  vuetify: {
    moduleOptions: {
      // check https://nuxt.vuetifyjs.com/guide/server-side-rendering.html
      ssrClientHints: {
        reloadOnFirstRequest: false,
        viewportSize: false,
        prefersColorScheme: false,

        prefersColorSchemeOptions: {
          useBrowserThemeOnly: true,
        },
      },

      // /* If customizing sass global variables ($utilities, $reset, $color-pack, $body-font-family, etc) */
      // disableVuetifyStyles: true,
      styles: {
        configFile: 'assets/settings.scss',
      },
    },
  },
  content: {
    renderer: {
      anchorLinks: { h2: false, h3: false, h4: false }
    },
    preview: {
      dev: true
    },
    build: {
      markdown: {
        highlight: {
          langs: ["json", "python", "shell", "bash"]
        }
      }
    }
  }
})