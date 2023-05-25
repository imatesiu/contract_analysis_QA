<template>
  <div id="app">
    <template v-if="showIntro">
      <!-- Introductory page content -->
      <div class="intro-container">
        <h1 class="intro-heading">ON - DEMAND NER INTRODUCTORY PAGE</h1>
        <div class="intro-text">
          <p><span class="intro-highlight">[Contesto]</span> Questa tesi si propone di contribuire al campo della ricerca
            sull'analisi di documenti legali attraverso l'applicazione di metodologie basate sul Natural Language
            Processing (NLP).</p>
          <p><span class="intro-highlight">[Problema]</span> A causa dell'ampia mole e della complessità dei contenuti di
            tali documenti, la consultazione e l'individuazione di informazioni chiave al loro interno richiedono spesso
            un notevole dispendio di tempo ed energie. Inoltre, l'approccio tradizionale di Named Entity Recognition
            (NER), che estrae informazioni semantiche da testi non strutturati, è statico e poco adattabile al dominio
            specifico del linguaggio legale.</p>
          <p><span class="intro-highlight">[Soluzione]</span> Questa analisi si propone di semplificare lo studio e la
            ricerca di informazioni da parte degli esperti legali mediante lo sviluppo di uno strumento di analisi in
            grado di eseguire non solo tecniche di analisi statiche come la Named Entity Recognition, ma anche un sistema
            di Question Answering, che consente di rispondere automaticamente a domande formulate in linguaggio naturale.
          </p>
          <p><span class="intro-highlight">[Risultati]</span> I risultati di questa tesi sono stati positivi in termini di
            performance, dimostrando che, nonostante alcune limitazioni, lo strumento può essere utilizzato per affrontare
            i problemi precedentemente menzionati. I test sono stati condotti su un set di documenti reali attraverso
            l'impiego di tecniche di prompt engineering, una disciplina relativamente nuova che consente di sviluppare e
            ottimizzare i prompt per sfruttare in modo efficiente modelli linguistici (LM) in una vasta gamma di
            applicazioni e argomenti di ricerca.</p>
          <p><span class="intro-highlight">[Contributo]</span> Questo lavoro rappresenta la prima proposta di un approccio
            di Named Entity Recognition (NER) flessibile, rapido e intuitivo specificamente adattato all'analisi di
            documenti legali.</p>
        </div>
        <button class="btn btn-primary start-button" @click="startMainComponent">Start</button>
      </div>
    </template>

    <MainComponent v-else />
  </div>
</template>

<style>
.intro-container {
  background-color: #f1f1f1;
  padding: 20px;
  border-radius: 10px;
}

.intro-heading {
  color: #333;
  font-size: 28px;
  margin-bottom: 20px;
}

.intro-text {
  color: #555;
  font-size: 16px;
  margin-bottom: 20px;
}

.intro-highlight {
  color: #ff6600;
  font-weight: bold;
}

.start-button {
  margin-top: 10px;
}</style>


<script>
import MainComponent from './components/MainComponent.vue'; // Importing the MainComponent
import '@fortawesome/fontawesome-free/css/all.min.css'; // Importing FontAwesome CSS
import 'bootstrap/dist/css/bootstrap.css'; // Importing Bootstrap CSS
import 'bootstrap/dist/js/bootstrap.js'; // Importing Bootstrap JS

export default {
  components: {
    MainComponent, // Registering the MainComponent as a child component
  },
  data() {
    return {
      showIntro: true, // Initially show the introductory page
    };
  },
  mounted() {
    const visitedIntro = sessionStorage.getItem('visitedIntro');
    if (visitedIntro) {
      this.showIntro = false;
    }
  },
  methods: {
    startMainComponent() {
      this.showIntro = false;
      sessionStorage.setItem('visitedIntro', 'true');
    },
  },
};
</script>
