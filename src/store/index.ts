// https://ionicframework.com/blog/managing-state-in-vue-with-vuex/

// https://github.com/mhartington/vuex-todo

import { InjectionKey } from 'vue';
import { createStore, useStore as baseUseStore, Store, MutationTree, } from 'vuex';

// interfaces for our State and todos
export type Selection = { eventId: number; providerId: number};
export type Purchase = { ticketId: number; email: string };
export type State = { selection: Selection; purchase: Purchase };

export const key: InjectionKey<Store<State>> = Symbol();
const state: State = {
  selection: {eventId: 0, providerId: 0},
  purchase: {ticketId: 0, email: ""},
};

/*
 * Mutations
 * How we mutate our state.
 * Mutations must be synchronous
 */
export const enum MUTATIONS {
  RESET_EVENT = 'RESET_EVENT',
  SET_EVENT = 'SET_EVENT',
  RESET_PURCHASE = 'RESET_PURCHASE',
  SET_PURCHASE = 'SET_PURCHASE',
}

const mutations: MutationTree<State> = {
  //[MUTATIONS.SET_EVENT](state, event: number, provider: number) {
    [MUTATIONS.SET_EVENT](state, selection: Selection ) {
      state.selection.eventId = selection.eventId;
      state.selection.providerId = selection.providerId;
    },
    [MUTATIONS.RESET_EVENT](state) {
      state.selection.eventId = 0;
      state.selection.providerId = 0;
    },
    [MUTATIONS.SET_PURCHASE](state, purchase: Purchase ) {
      state.purchase.ticketId = purchase.ticketId;
      state.purchase.email = purchase.email;
    },
    [MUTATIONS.RESET_PURCHASE](state) {
      state.purchase.ticketId = 0;
      state.purchase.email = "";
    },
  };

/*
 * Actions
 * Perform async tasks, then mutate state
 */
/*
export const enum ACTIONS { ADD_RND_TODO = 'ADD_RND_TODO', }
const actions: ActionTree<State, any> = {
  [ACTIONS.ADD_RND_TODO](store) {
        const newTodo: Todo = {
          title: "title",
          id: Math.random(),
          note: "madmakfmakfmkefm"
        }
        store.commit(MUTATIONS.ADD_TODO, newTodo);
  },
};
*/

export const store = createStore<State>({ state, mutations });

// our own useStore function for types
export function useStore() {
  return baseUseStore(key);
}

