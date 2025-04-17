import MainPage from '~/components/MainPage.vue'
import { createMemoryHistory, createRouter } from 'vue-router'
export const router = createRouter(
    {
        history: createMemoryHistory(),
        routes: [
            { 
                path: '/#:project', 
                component: MainPage, 
                props: true 
            },
        ]
    }
)
export default router