<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>Tickets
        <img alt="logo" height="40" style="vertical-align:middle"  src="/assets/img/logo.png" > 
        </ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content >
      <ion-card>
      <ion-card-content>

      <div v-if="hasEvent">
        <Event 
          :date=getEvent.date 
          :time=getEvent.time 
          :title=getEvent.title 
          :text=getEvent.provider 
          :id=getEvent.id
          :icon=getEvent.category_id
          >
        </Event>

        <OrderForm @purchaseComplete="purchaseCompleted($event)"></OrderForm>
        <!--
        <ion-item>
        <Ion-button class="center-button" @click="presentActionSheet()">
          Buchen
        </Ion-button>
        </ion-item>
        -->
      </div>
      <div v-else> 
        <h2>Nichts ausgewählt!</h2>
        Bitte wähle zuerst eine Veranstaltung aus.
      </div>

      </ion-card-content>

      </ion-card>


    </ion-content>

  </ion-page>
</template>

<script lang="js">
import { IonPage, IonButton, IonHeader, IonToolbar, IonTitle, 
  IonContent,IonCard, IonCardContent,
  actionSheetController,
  } from '@ionic/vue';
import Event from '@/components/Event.vue';
import { defineComponent } from 'vue'; 

import { rocket, trash,  } from 'ionicons/icons';

// load all data from server and write to database
import DataStorage from "../services/dstore";

// https://next.vuex.vuejs.org/guide/composition-api.html#accessing-state-and-getters

import { useStore, Selection, MUTATIONS } from '../store';

// test
import OrderForm from '@/components/OrderForm.vue';

/* passing data from child to parent 
https://forum.vuejs.org/t/passing-data-back-to-parent/1201
https://dev.to/freakflames29/how-to-pass-data-from-child-to-parent-in-vue-js-2d9m
https://v3.vuejs.org/guide/migration/emits-option.html#_3-x-behavior
*/

export default  defineComponent ({
  name: 'Tickets',
  data () {
    return {
      //evnt: {},
      items : [],
      ds: "",
    }
  },
  components: { Event, IonHeader, IonToolbar, IonTitle, IonContent, IonPage,IonCard, IonCardContent, OrderForm  },
  methods: {
    purchase() {
      console.log("Buy ticket: ")
    },
    purchaseCompleted(result) {
        console.log("Completed: ",result,"status: ",
        result.status,", ticket: ",result.payload.ticket)
        if (result.status) {
          this.presentActionSheet()
        }
    },

    async presentActionSheet() {
      const actionSheet = await actionSheetController
        .create({
          header: 'Buchung',
          buttons: [
            {
              text: 'Bestätigen',
              icon: rocket,
              role: 'OK',
              handler: () => {
                this.purchase()
              }
            },
            {
              text: 'Abbrechen',
              icon: trash,
              role: 'cancel',
              handler: () => {
                console.log('Cancel clicked')
              },
            },
          ],
        });
      await actionSheet.present();
      const { role } = await actionSheet.onDidDismiss();
      console.log('onDidDismiss resolved with role', role);
    },
  },
  computed: {
    hasEvent() {
      return (this.store.state.selection.eventId != 0)
    },
    getEvent() {
      if (this.store.state.selection.eventId != 0) {
        const evnt = this.items[this.store.state.selection.eventId - 1] 
        //console.log("event item: ",evnt)
        return evnt
      } else 
      return {x:1}
    }
  },
  async beforeMount() {
    this.ds = await DataStorage.getInstance()
    const providerString = await this.ds.getItem("provider") || "[]"
    const providers = JSON.parse(providerString)
    const itemString = await this.ds.getItem("event") || "[]"
    const items = JSON.parse(itemString)
    for (let i=0; i < items.length; i++){
      const id = items[i].provider_id - 1
      const name = providers[id].name
      //console.log("i: ",i,", id: ",id, ", name: ",name)
      items[i].provider = name
    }
    this.items = items
  },
  // store
  setup() {
    const store = useStore();
    return { store };
  },
})

</script>

<style scoped>

.center-button {
  display: block;
  margin: auto;
}

.center-button>button {
  padding: 1em;
}

</style>