<template>
    <div>
        <!-- This is the navbar section for the page -->
        <nav class="navbar sticky-top bg-body-tertiary" style="background-color: #006cf9d9;">
            <div class="container-fluid">
                ON-DEMAND NER <!-- This is the header text for the navbar -->
            </div>
        </nav>

        <!-- The following code creates a toast notification for when a file has been uploaded successfully. -->
        <div v-if="showToast">
            <div class="toast show fade bg-success p-3 position-fixed" role="alert" aria-live="assertive"
                aria-atomic="true">
                <div class="toast-header">
                    <strong class="me-auto">UPLOAD FILE</strong>
                    <button type="button" class="btn-close" data-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    File uploaded correctly!
                </div>
            </div>
        </div>

        <!-- The following code creates a toast notification for when a file has been edited successfully. -->
        <div v-if="showEdited">
            <div class="toast show fade bg-success p-3 position-fixed" role="alert" aria-live="assertive"
                aria-atomic="true">
                <div class="toast-header">
                    <strong class="me-auto">EDIT FILE</strong>
                    <button type="button" class="btn-close" data-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    File edited correctly!
                </div>
            </div>
        </div>

        <!-- The following code creates a toast notification for when a configuration has been loaded successfully. -->
        <div v-if="showLoad">
            <div class="toast show fade bg-success p-3 position-fixed" role="alert" aria-live="assertive"
                aria-atomic="true">
                <div class="toast-header">
                    <strong class="me-auto">LOAD CONFIGURATION</strong>
                    <button type="button" class="btn-close" data-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    Configuration loaded correctly!
                </div>
            </div>
        </div>

        <!-- The following code creates a toast notification for when a configuration has been changed successfully. -->
        <div v-if="showChange">
            <div class="toast show fade bg-success p-3 position-fixed" role="alert" aria-live="assertive"
                aria-atomic="true">
                <div class="toast-header">
                    <strong class="me-auto">CHANGE CONFIGURATION</strong>
                    <button type="button" class="btn-close" data-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    Configuration changed correctly!
                </div>
            </div>
        </div>

        <!-- The following code creates a toast notification for when entities have been deleted successfully. -->
        <div v-if="showDelete">
            <div class="toast show fade bg-success p-3 position-fixed" role="alert" aria-live="assertive"
                aria-atomic="true">
                <div class="toast-header">
                    <strong class="me-auto">DELETE ENTITIES</strong>
                    <button type="button" class="btn-close" data-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    Entities deleted correctly!
                </div>
            </div>
        </div>

        <!-- The following code creates a toast notification for when a question has been saved successfully. -->
        <div v-if="showSave">
            <div class="toast show fade bg-success p-3 position-fixed" role="alert" aria-live="assertive"
                aria-atomic="true">
                <div class="toast-header">
                    <strong class="me-auto">SAVE QUESTION</strong>
                    <button type="button" class="btn-close" data-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    Question saved correctly!
                </div>
            </div>
        </div>

        <!-- This is a row section of the page that contains form elements -->
        <div class="row justify-content-center">
            <div class="col-md-8">

                <!-- This is the form that allows the user to upload a file -->
                <div v-if="upload">
                    <form @submit.prevent="uploadFile();">

                        <!-- This is the file input field where user can select a file -->
                        <div class="mb-3">
                            <label for="file-input" class="form-label">Choose file:</label>
                            <input id="file-input" type="file" class="form-control" ref="file" accept=".pdf,.docx,.xlsx">
                        </div>

                        <!-- This is the language selection dropdown for the user -->
                        <div class="mb-3">
                            <label for="language-select" class="form-label">Select language:</label>
                            <select id="language-select" class="form-select" v-model="language">
                                <option value="en">English</option>
                                <option value="it">Italian</option>
                            </select>
                        </div>

                        <!-- This is the upload button that triggers file upload action -->
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary"
                                @click="dictionaryObj = null; str_dict = null; loaded = false; selectedEntities = []; high_entities = []; colors = []; high_text = null; colors = []; text = null;">
                                Upload new file
                            </button>
                        </div>
                    </form>

                    <!-- This is the loading spinner that is shown when file is being uploaded -->
                    <div v-if="loading" class="d-flex align-items-center" style="margin: 10px;">
                        <strong>Loading upload...</strong>
                        <div class="spinner-border ms-auto" role="status" aria-hidden="true"></div>
                    </div>

                </div>


                <div v-else-if="text"> <!-- Renders the selected entities only if there are any -->

                    <button class="btn btn-outline-warning float-end" @click="reload"
                        style="margin-top: 5px; margin-bottom: 10px">UPLOAD NEW FILE</button>


                    <h2>Extracted text: </h2> {{ txt_file }}

                    <div class="mb-3">
                        <!-- If editing is not enabled and no high text is present, display a readonly textarea with the extracted text -->
                        <textarea v-if="!editing && !high_text" v-model="text" class="form-control" style="height: 300px;"
                            readonly></textarea>

                        <!-- If editing is enabled and no high text is present, display an editable textarea with the extracted text -->
                        <textarea v-else-if="editing && !high_text" v-model="editText" class="form-control"
                            style="height: 300px;"></textarea>

                        <!-- If high text is present, display a div containing the highlighted text with entity colors -->
                        <div v-if="high_text" v-html="high_text" class="form-control"
                            style="height: 300px; overflow: auto;"></div>

                        <!-- Button to reset the selected entities and their highlighting -->
                        <button v-if="high_text"
                            @click="selectedEntities = []; high_entities = []; colors = []; high_text = null; colors = []; question = null; score = null; scrollDown();"
                            class="btn btn-danger" style="margin-top: 5px;">Reset</button>
                        <button v-if="question && high_text" type="button" class="btn btn-warning" data-bs-toggle="modal"
                            data-bs-target="#staticBackdrop" style="margin-top: 5px; margin-left: 10px;">
                            Save Question
                        </button>

                        <span v-if="score"> Answer Score: {{ this.score }}</span>

                        <div v-if="saving_question" class="d-flex align-items-center" style="margin: 10px;">
                            <strong>Loading configuration...</strong>
                            <div class="spinner-border ms-auto" role="status" aria-hidden="true"></div>

                        </div>
                    </div>

                    <!-- If entity colors are present, display a series of color boxes representing each entity with its associated text -->
                    <div v-if="colors.length > 0">
                        <div class="legend mb-3">
                            <div class="legend-title">Legend:</div>
                            <div v-for="(color, index) in colors" :key="index" class="legend-item">
                                <div class="color-box" :style="{ backgroundColor: color }"></div>
                                <div class="entity-name">{{ high_entities[index] }}</div>
                            </div>
                        </div>

                    </div>

                    <div class="mb-3">
                        <!-- If editing is not enabled and no high text is present and the file is not yet loaded, display an "Edit" button -->
                        <button v-if="!editing && !high_text" @click="editText = text; editing = true"
                            class="btn btn-primary">Edit</button>

                        <!-- If editing is enabled, display "Save" and "Cancel" buttons -->
                        <div v-if="editing">
                            <button @click="updateText" class="btn btn-success me-2" style="margin: 5px">Save</button>
                            <button @click="editing = false" class="btn btn-secondary" style="margin: 5px">Cancel</button>

                            <div v-if="loading_editing" class="d-flex align-items-center" style="margin: 10px;">
                                <strong>Loading changes...</strong>
                                <div class="spinner-border ms-auto" role="status" aria-hidden="true"></div>

                            </div>
                        </div>

                        <!-- Modal -->
                        <!-- Define a modal dialog with an id of "exampleModal" and set some accessibility attributes -->
                        <div class="modal fade" id="exampleModal" tabindex="-1" aria-labelledby="changeCNF"
                            aria-hidden="true">
                            <!-- Define a modal dialog that spans the width of its parent element -->
                            <div class="modal-dialog">
                                <!-- Define the content of the modal dialog -->
                                <div class="modal-content">
                                    <!-- Define the header of the modal dialog with a title and a close button -->
                                    <div class="modal-header">
                                        <h1 class="modal-title fs-5" id="changeCNF">Choose configuration</h1>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal"
                                            aria-label="Close"></button>
                                    </div>
                                    <!-- Define the body of the modal dialog -->
                                    <div class="modal-body">
                                        <!-- If the selected language is Italian, display a select element for Italian configurations -->
                                        <div v-if="language == 'it'" class="form-group">
                                            <label for="cnf-it-select">Available configuration:</label>
                                            <select id="cnf-it-select" v-model="config_to_change" class="form-control">
                                                <option v-for="conf in available_configs_it" :key="conf">{{ conf }}</option>
                                            </select>
                                        </div>
                                        <!-- If the selected language is not Italian, display a select element for English configurations -->
                                        <div v-else class="form-group">
                                            <label for="cnf-en-select">Available configuration:</label>
                                            <select id="cnf-en-select" v-model="config_to_change" class="form-control">
                                                <option v-for="conf in available_configs_en" :key="conf">{{ conf }}</option>
                                            </select>
                                        </div>
                                    </div>
                                    <!-- Define the footer of the modal dialog with a "Close" and "Save Changes" button -->
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary"
                                            data-bs-dismiss="modal">Close</button>
                                        <button type="button" class="btn btn-primary" data-bs-dismiss="modal"
                                            @click="changeConfig(), loaded = false">Save changes</button>
                                    </div>
                                </div>
                            </div>
                        </div>


                        <!-- This div displays the current configuration -->
                        <div v-if="dictionaryObj" class="my-3">
                            <h6>Current configuration:</h6> {{ file_config }}
                            <div v-if="loading_change" class="d-flex align-items-center" style="margin: 10px;">
                                <strong>Loading configuration...</strong>
                                <div class="spinner-border ms-auto" role="status" aria-hidden="true"></div>

                            </div>
                        </div>
                    </div>

                    <div v-if="loaded == true"> <!-- Only if is been loaded a configuration -->

                        <div v-if="dictionaryObj" class="mt-3">

                            <div class="container">
                                <table class="table">
                                    <thead>
                                        <!-- Table header row -->
                                        <tr>
                                            <th scope="col">Entity</th>
                                            <th scope="col">Question</th>
                                            <th scope="col">Select</th>
                                            <th scope="col">Model</th>
                                            <th scope="col">Delete</th>
                                        </tr>
                                    </thead>

                                    <tbody>
                                        <!-- Table body row, loops through each key-value pair in dictionaryObj -->
                                        <tr v-for="(value, key) in dictionaryObj" :key="key">
                                            <!-- Entity name column -->
                                            <td>{{ key }}</td>
                                            <!-- Entity question column -->
                                            <td>{{ value }}</td>
                                            <!-- Checkbox column to select the entity -->
                                            <td>
                                                <div class="form-check">
                                                    <input class="form-check-input" type="checkbox"
                                                        v-model="selectedEntities" :value="key">
                                                </div>
                                            </td>
                                            <!-- Model column displaying the NER model used for each entity -->
                                            <td>
                                                {{ model_entity[key] }}
                                            </td>
                                            <!-- Checkbox column to delete the entity (only displayed if the model used is not Spacy) -->
                                            <td>
                                                <div class="form-check" v-if="model_entity[key] != 'Spacy'">
                                                    <input class="form-check-input" type="checkbox"
                                                        v-model="todelete_entities" :value="key">
                                                </div>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>


                                <!-- This section displays the list of selected entities and provides options to filter or reset them. -->
                                <div>
                                    <div v-if="selectedEntities.length > 0" class="my-4" style="margin: 10px;">
                                        <h6>Selected Entities:</h6>
                                        <ul class="list-group">
                                            <li class="list-group-item" v-for="entity in selectedEntities" :key="entity">{{
                                                entity }}</li>
                                        </ul>
                                        <button class="btn btn-primary mt-3" @click="filter()">Filter Selected</button>
                                        <button class="btn btn-danger mt-3" @click="selectedEntities = []">Reset
                                            Selected</button>
                                    </div>

                                    <!-- This section displays the list of entities selected for deletion and provides options to delete or reset them. -->
                                    <div v-if="todelete_entities.length > 0" class="my-4" style="margin: 10px;">
                                        <h6>Delete Entities:</h6>
                                        <ul class="list-group">
                                            <li class="list-group-item" v-for="entity in todelete_entities" :key="entity">{{
                                                entity }}</li>
                                        </ul>
                                        <button type="button" class="btn btn-danger mt-3" data-bs-toggle="modal"
                                            data-bs-target="#exampleModal2">
                                            Delete Selected
                                        </button>
                                        <button class="btn btn-success mt-3" @click="todelete_entities = []">Reset
                                            Selected</button>

                                        <!-- This section displays a confirmation modal for deleting selected entities. -->
                                        <div class="modal fade" id="exampleModal2" tabindex="-1"
                                            aria-labelledby="exampleModal2Label" aria-hidden="true">
                                            <div class="modal-dialog">
                                                <div class="modal-content">
                                                    <div class="modal-header">
                                                        <h1 class="modal-title fs-5" id="exampleModal2Label">Are you sure?
                                                        </h1>
                                                        <button type="button" class="btn-close" data-bs-dismiss="modal"
                                                            aria-label="Close"></button>
                                                    </div>
                                                    <div class="modal-body">
                                                        Do you really want to delete the selected entities?
                                                    </div>
                                                    <div class="modal-footer">
                                                        <button type="button" class="btn btn-secondary"
                                                            data-bs-dismiss="modal">Close</button>
                                                        <button type="button" class="btn btn-primary"
                                                            data-bs-dismiss="modal" @click="deleteEn">Yes</button>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                            </div>

                            <div>
                                <!-- This button will trigger the configuration change when clicked -->
                                <button v-if="dictionaryObj" type="button" class="btn btn-primary" data-bs-toggle="modal"
                                    data-bs-target="#exampleModal"
                                    @click="selectedEntities = []; high_text = null; colors = [];">
                                    Change Configuration...
                                </button>

                                <button v-if="question && high_text" type="button" class="btn btn-warning"
                                    data-bs-toggle="modal" data-bs-target="#staticBackdrop" style="margin-left: 10px">
                                    Save Question
                                </button>

                                <button v-if="dictionaryObj" class="btn btn-outline-success me-2" @click="downloadJson"
                                    style="margin: 5px">Download JSON</button>

                                <h5>Type your own question:</h5>

                                <textarea class="form-control mb-3" v-model="question" rows="2"
                                    placeholder="Insert your question here"></textarea>

                                <!-- If language is Italian, show Italian model select dropdown -->
                                <div v-if="language === 'it'" class="mb-3">
                                    <label for="model-en-select">Available Model:</label>
                                    <select id="model-en-select" class="form-select" v-model="model_choosen">
                                        <option v-for="model in model_available_it" :key="model">{{ model }}</option>
                                    </select>
                                </div>

                                <!-- If language is not Italian, show English model select dropdown -->
                                <div v-else class="mb-3">
                                    <label for="model-it-select">Available Model:</label>
                                    <select id="model-it-select" class="form-select" v-model="model_choosen">
                                        <option v-for="model in model_available_en" :key="model">{{ model }}</option>
                                    </select>
                                </div>


                                <!-- Button to initiate the question answering process -->
                                <button class="btn btn-primary"
                                    @click="score = null; high_text = null; question_answering();">GO</button>

                                <!-- Display loading message while the answer is being computed -->
                                <div v-if="loading_qa" class="d-flex align-items-center" style="margin: 10px;">
                                    <strong>Computing answer...</strong>
                                    <div class="spinner-border ms-auto" role="status" aria-hidden="true"></div>
                                </div>

                                <!-- The modal window for adding an entity -->
                                <div class="modal fade" id="staticBackdrop" data-bs-backdrop="static"
                                    data-bs-keyboard="false" tabindex="-1" aria-labelledby="staticBackdropLabel"
                                    aria-hidden="true">
                                    <div class="modal-dialog">
                                        <div class="modal-content">
                                            <!-- The header of the modal window -->
                                            <div class="modal-header">
                                                <h1 class="modal-title fs-5" id="staticBackdropLabel">Add Entity</h1>
                                                <button type="button" class="btn-close" data-bs-dismiss="modal"
                                                    aria-label="Close"></button>
                                            </div>
                                            <!-- The body of the modal window, containing the form for adding the entity -->
                                            <div class="modal-body">
                                                <form>
                                                    <!-- Input field for entity name -->
                                                    <div class="mb-3">
                                                        <label for="entity-name" class="form-label">Entity Name:</label>
                                                        <input type="text" id="entity-name" v-model="name_entity"
                                                            class="form-control">
                                                    </div>
                                                    <!-- Dropdown menu to select the configuration to add the question to -->
                                                    <div class="mb-3">
                                                        <label for="check-config" class="form-label">Select an existing
                                                            configuration to add question to:</label>
                                                        <!-- Language-specific options for the dropdown menu -->
                                                        <div v-if="language == 'it'">
                                                            <select id="cnf-it-select" v-model="config_to_change"
                                                                class="form-select">
                                                                <!-- Option elements for Italian configuration names -->
                                                                <option v-for="conf in available_configs_it" :key="conf">{{
                                                                    conf }}</option>
                                                            </select>
                                                        </div>
                                                        <div v-else>
                                                            <select id="cnf-en-select" v-model="config_to_change"
                                                                class="form-select">
                                                                <!-- Option elements for English configuration names -->
                                                                <option v-for="conf in available_configs_en" :key="conf">{{
                                                                    conf }}</option>
                                                            </select>
                                                        </div>
                                                    </div>
                                                    <!-- Checkbox to indicate if creating a new configuration -->
                                                    <div class="form-check mb-3">
                                                        <input type="checkbox" id="new" v-model="new_config" :value="true"
                                                            class="form-check-input">
                                                        <label for="new" class="form-check-label">New config?</label>
                                                    </div>
                                                    <!-- Input field for new configuration name, only shown if checkbox is selected -->
                                                    <div v-if="new_config" class="mb-3">
                                                        <div class="form-check">
                                                            <input type="radio" id="option1" name="options"
                                                                class="form-check-input" checked v-model="option_save"
                                                                :value="1">
                                                            <label for="option" class="form-check-label">New
                                                                configuration</label>
                                                        </div>

                                                        <div class="form-check">
                                                            <input type="radio" id="option2" name="options"
                                                                class="form-check-input" v-model="option_save" :value="0">
                                                            <label for="option" class="form-check-label">From this
                                                                configuration</label>
                                                        </div>
                                                        <label for="config-name" class="form-label">Config Name:</label>
                                                        <input type="text" id="config-name" v-model="name_new_config"
                                                            class="form-control">
                                                    </div>
                                                </form>
                                            </div>
                                            <!-- The footer of the modal window, containing buttons to save or close the window -->
                                            <div class="modal-footer">
                                                <button type="button" @click.prevent="saveQuestion" class="btn btn-primary"
                                                    data-bs-dismiss="modal">Save</button>
                                                <button type="button" class="btn btn-secondary"
                                                    data-bs-dismiss="modal">Close</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                            </div>

                        </div>

                    </div>

                    <!-- This div is only shown if the dictionaryObj is not loaded -->
                    <div v-else class="d-flex justify-content-center my-3">
                        <!-- Button to load the CNF if it has not been loaded yet -->
                        <button v-if="dictionaryObj == null" class="btn btn-primary" @click="loadCnf();">Load
                            Configuration... (last used or default)</button>
                    </div>

                    <!-- This div is only shown while the configuration is being loaded -->
                    <div v-if="loading_config" class="d-flex align-items-center" style="margin: 10px;">
                        <!-- Text to indicate that the configuration is being loaded -->
                        <strong>Loading configuration...</strong>
                        <!-- Spinner animation to indicate that the configuration is being loaded -->
                        <div class="spinner-border ms-auto" role="status" aria-hidden="true"></div>
                    </div>

                </div>
            </div>
        </div>

        <div>
            <a href="#" class="btn btn-primary btn-lg back-to-bottom" role="button">
                <i class="fas fa-chevron-down"></i>
            </a>

            <a href="#" class="btn btn-primary btn-lg back-to-top" role="button">
                <i class="fas fa-chevron-up"></i>
            </a>
        </div>
    </div>
</template>

<script>
// This module imports the Axios library, which is a JavaScript library used to make HTTP requests from node.js
import axios from "axios";
import $ from 'jquery';
import '@fortawesome/fontawesome-free/css/all.min.css';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.js';

// Export a default object containing a data function
export default {
    data() {
        // Initialize properties in the returned object
        return {
            // A string that will hold the text entered by the user, initially set to null
            text: null,
            // A file object that will hold the uploaded text file, initially set to null
            txt_file: null,
            // A boolean value that indicates whether the user is currently editing text, initially set to false
            editing: false,
            // A string that will hold the edited text, initially set to null
            editText: null,
            // A file object that will hold the uploaded configuration file, initially set to null
            file_uploaded: null,
            // A string that indicates the language of the text, initially set to "it" (Italian)
            language: 'en',
            // An object that will hold the dictionary of entities found in the text, initially set to null
            dictionaryObj: null,
            // An array that will hold the currently selected entities, initially set to an empty array
            selectedEntities: [],
            // An array that will hold the entities to be deleted, initially set to an empty array
            todelete_entities: [],
            // A string that will hold the text with the selected entities highlighted, initially set to null
            high_text: null,
            // A boolean value that indicates whether the data has finished loading, initially set to false
            loaded: false,
            // An array that will hold the colors for the highlighted entities, initially set to an empty array
            colors: [],
            // An array that will hold the entities that have been highlighted, initially set to an empty array
            high_entities: [],
            // An array that will hold the available configurations for English language, initially set to an empty array
            available_configs_en: [],
            // An array that will hold the available configurations for Italian language, initially set to an empty array
            available_configs_it: [],
            // A string that indicates the configuration to be changed, initially set to null
            config_to_change: null,
            // A string that holds the question to be answered, initially set to null
            question: null,
            // A string that indicates the chosen language model, initially set to null
            model_choosen: null,
            // An array that holds the available English language models, initially set to an array of model names
            model_available_en: ["deepset/roberta-base-squad2", "distilbert-base-cased-distilled-squad", "bert-large-uncased-whole-word-masking-finetuned-squad", "squirro/albert-base-v2-squad_v2", "ahotrod/electra_large_discriminator_squad2_512", "cecchiara/bert-finetuned-squad-accelerate"],
            // An array that holds the available Italian language models, initially set to an array of model names
            model_available_it: ["anakin87/electra-italian-xxl-cased-squad-it"],
            // A string that holds the answer to the question, initially set to null
            answer: null,
            // A file object that holds the uploaded configuration file, initially set to null
            file_config: null,
            // A string that indicates the model entity, initially set to null
            model_entity: null,
            // A string that indicates the name of the entity, initially set to null
            name_entity: null,
            // A boolean that indicates if is necessary create a new configuration, initially set to false
            new_config: false,
            // A string tha indicates tha name of the configuration to create, initially set to null
            name_new_config: null,
            // An integer that indicate the result of the response
            code: 0,
            // A string that indicate the dictionary_obj, initially set to null
            str_dict: null,
            // Flag for upload-file spinner
            loading: false,
            //Flag for edit-file spinner
            loading_editing: false,
            //Flag for load-config spinner
            loading_config: false,
            //Flag for qa spinner
            loading_qa: false,
            //Flag for change-config spinner
            loading_change: false,
            //Flag for save-question spinner
            saving_question: false,

            showToast: false,

            showEdited: false,

            showLoad: false,

            showChange: false,

            showDelete: false,

            showSave: false,

            upload: false,

            score: null,

            option_save: 0,
        };
    },

    methods: {

        reload() {
            location.reload();
        },

        // this function upload a file 
        uploadFile() {

            this.loading = true;
            // Create a new FormData object.
            let formData = new FormData();
            // Add the file object and the language property to the form data object.
            formData.append("file", this.$refs.file.files[0]);
            formData.append("language", this.language);
            // Get the file object from the input element.
            let file = this.$refs.file.files[0];
            // Check the file type to determine which API endpoint to call.
            if (file == null) {
                alert("Choose a file!");
                this.loading = false;
            } else {
                if (file.type === "application/pdf") {
                    // Make a POST request to the PDF upload API endpoint.
                    axios
                        .post("http://localhost:8000/api/pdf-upload/", formData)
                        .then(response => {
                            // If the language is Italian, set the text and TXT file to the Italian versions.
                            if (this.language == "it") {
                                this.text = response.data.pdf_text_it;
                                this.txt_file = response.data.txt_file_pdf_it;
                            }
                            // Otherwise, set the text and TXT file to the English versions.
                            else {
                                this.text = response.data.pdf_text_en;
                                this.txt_file = response.data.txt_file_pdf_en;
                            }
                            // Set the file_uploaded property to the title of the uploaded file.
                            this.file_uploaded = response.data.title;

                            this.loading = false;
                            setTimeout(() => {
                                window.scrollTo(0, document.body.scrollHeight);
                            }, 500);

                            this.showToast = true;

                            setTimeout(() => {
                                this.showToast = false;
                            }, 2000);
                            this.upload = false;
                        })
                        // If there was an error, log it to the console and show an alert with the error message
                        .catch(error => {
                            console.log(error);
                            alert(error);
                            this.loading = false;
                        });
                }
                else if (file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document" || file.type === "application/msword") {
                    // Make a POST request to the Word upload API endpoint.
                    axios
                        .post("http://localhost:8000/api/word-upload/", formData)
                        .then(response => {
                            // If the language is Italian, set the text and TXT file to the Italian versions.
                            if (this.language === "it") {
                                this.text = response.data.docx_text_it;
                                this.txt_file = response.data.txt_file_docx_it;
                            }
                            // Otherwise, set the text and TXT file to the English versions.
                            else {
                                this.text = response.data.docx_text_en;
                                this.txt_file = response.data.txt_file_docx_en;
                            }
                            // Set the file_uploaded property to the title of the uploaded file.
                            this.file_uploaded = response.data.title;
                            this.loading = false;
                            setTimeout(() => {
                                window.scrollTo(0, document.body.scrollHeight);
                            }, 500);

                            this.showToast = true;

                            setTimeout(() => {
                                this.showToast = false;
                            }, 2000);
                            this.upload = false;
                        })
                        // If there was an error, log it to the console and show an alert with the error message
                        .catch(error => {
                            console.log(error);
                            alert(error);
                            this.loading = false;
                        });
                }
                else if (file.type === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") {
                    // Make a POST request to the XLSX upload API endpoint.
                    axios
                        .post("http://localhost:8000/api/xlsx-upload/", formData)
                        .then(response => {
                            // If the language is Italian, set the text and TXT file to the Italian versions.
                            if (this.language === "it") {
                                this.text = response.data.xlsx_text_it;
                                this.txt_file = response.data.txt_file_xlsx_it;
                            }
                            // Otherwise, set the text and TXT file to the English versions.
                            else {
                                this.text = response.data.xlsx_text_en;
                                this.txt_file = response.data.txt_file_xlsx_en;
                            }
                            // Set the file_uploaded property to the title of the uploaded file.
                            this.file_uploaded = response.data.title;
                            this.loading = false;
                            setTimeout(() => {
                                window.scrollTo(0, document.body.scrollHeight);
                            }, 500);

                            this.showToast = true;

                            setTimeout(() => {
                                this.showToast = false;
                            }, 2000);
                            this.upload = false;

                        })
                        // If there was an error, log it to the console and show an alert with the error message
                        .catch(error => {
                            console.log(error);
                            alert(error);
                            this.loading = false;
                        });
                }
                else {
                    // If the file type is not supported, display an error message.
                    alert("Unsupported file type: only .pdf, .docx or .xlsx !!!");
                    this.loading = false;

                }
                // Make a POST request to the get-config API endpoint to retrieve the available configurations and sets the relative list based on the language

                axios.post("http://localhost:8000/api/get-config/", { "language": this.language })
                    .then(response => {
                        if (this.language == "it") {
                            this.available_configs_it = response.data.configs;
                        }
                        else {
                            this.available_configs_en = response.data.configs;
                        }
                        // If there was an error, log it to the console and show an alert with the error message
                    }).catch(error => {
                        console.log(error);
                        alert(error);
                        this.loading = false;
                    });
            }

        },
        // this function modify the text
        updateText() {
            this.loading_editing = true;
            this.scrollDown();
            // Make a POST request to the specified API endpoint with the following data:
            axios.post("http://localhost:8000/api/update-text/", {
                // The text to be edited
                text_toEdit: this.editText,
                // The name of the file to be edited
                file_toEdit: this.txt_file,
                // The source file from which the original text was obtained
                file_source: this.file_uploaded,
                // The language of the text
                language: this.language
            })
                // If the request was successful, update the text and file variables and disable editing mode
                .then(response => {
                    this.text = this.editText;
                    this.txt_file = response.data.txt_file_edited;
                    this.editing = false;
                    this.loading_editing = false;
                    this.showEdited = true;

                    setTimeout(() => {
                        this.showEdited = false;
                    }, 2000);

                })
                // If there was an error, log it to the console and show an alert with the error message
                .catch(error => {
                    console.log(error);
                    alert(error);
                    this.loading_editing = false;
                });


        },
        // This function loads a configuration file for the NER model
        loadCnf() {
            this.dictionaryObj = null;
            this.loading_config = true;
            this.scrollDown();
            // Send a POST request to the specified API endpoint with the following data:
            axios.post("http://localhost:8000/api/load-config/", {
                // The path to the text file to be analyzed
                file_txt_path: this.txt_file,
                // The language of the text
                language: this.language,
                // The text to be analyzed
                text: this.text,
                // The source file from which the original text was obtained
                f_up: this.file_uploaded
            })
                // If the request was successful, update some variables with the response data
                .then(response => {
                    this.dictionaryObj = JSON.parse(response.data.jsonner_str);
                    this.file_config = response.data.jsonNER;
                    this.loaded = true;
                    this.model_entity = JSON.parse(response.data.entity_model_current);
                    this.str_dict = response.data.jsondict_str;
                    this.loading_config = false;
                    this.scrollDown();

                    this.showLoad = true;

                    setTimeout(() => {
                        this.showLoad = false;
                    }, 2000);

                })
                // If there was an error, log it to the console and show an alert with the error message
                .catch(error => {
                    console.log(error);
                    alert(error);
                    this.loading_config = false;
                });


        },
        // This function filters the NER output by a selected set of entities
        filter() {
            // Send a POST request to the specified API endpoint with the following data:
            axios.post("http://localhost:8000/api/filter/", {
                // The path to the text file to be analyzed
                file_txt_path: this.txt_file,
                // The language of the text
                language: this.language,
                // The text to be analyzed
                text: this.text,
                // The set of entities to filter by
                selectedEn: this.selectedEntities
            })
                // If the request was successful, update some variables with the response data
                .then(response => {
                    this.high_text = response.data.high;
                    this.colors = response.data.colors;
                    this.high_entities = response.data.ent;
                    this.question = null;
                    setTimeout(() => {
                        window.scrollTo(0, document.body.scrollTop);
                    }, 500);
                })
                // If there was an error, log it to the console and show an alert with the error message
                .catch(error => {
                    console.log(error);
                    alert(error);
                });
        },
        // This function performs question-answering on the given text
        question_answering() {
            this.loading_qa = true;
            this.scrollDown();
            // If the language is Italian and no model has been chosen, default to 'anakin87/electra-italian-xxl-cased-squad-it'
            if (this.language == "it" & this.model_choosen == null) {
                this.model_choosen = "anakin87/electra-italian-xxl-cased-squad-it";
            }
            else {
                // Otherwise, if no model has been chosen, default to 'deepset/roberta-base-squad2'
                if (this.model_choosen == null)
                    this.model_choosen = "deepset/roberta-base-squad2";
            }
            // Send a POST request to the specified API endpoint with the following data:
            axios.post("http://localhost:8000/api/qa/", {
                // The question to be answered
                question: this.question,
                // The name of the question-answering model to use
                model: this.model_choosen,
                // The text to be analyzed
                text: this.text

            })
                // If the request was successful, update some variables with the response data
                .then(response => {
                    this.high_text = response.data.high_qa;
                    this.high_entities = [];
                    this.colors = [];
                    this.answer = response.data.answer;
                    this.selectedEntities = [];

                    this.score = response.data.score;

                    this.loading_qa = false;

                    setTimeout(() => {
                        window.scrollTo(0, document.body.scrollTop - 30);
                    }, 500);
                })
                // If there was an error, log it to the console and show an alert with the error message
                .catch(error => {
                    console.log(error);
                    alert(error);
                    this.loading_qa = false;
                });


        },
        // this function save a question 
        saveQuestion() {
            this.saving_question = true;
            // Send a POST request to the API endpoint to save the question and answer
            axios.post("http://localhost:8000/api/save-question/", {
                name_entity: this.name_entity,
                model: this.model_choosen,
                question: this.question,
                answer: this.answer,
                txt_path: this.txt_file,
                language: this.language,
                config_to_change: this.config_to_change,
                new_c: this.new_config,
                name_config_new: this.name_new_config,
                file_c: this.file_config, // The configuration file being used
                option: this.option_save
            })
                .then(response => {
                    // If the response indicates an error, display an alert
                    if (response.data.cod == -1) {
                        alert(response.data.res);
                        this.saving_question = false;
                    }
                    // Otherwise, update the state variables and retrieve the updated configuration and available configurations
                    else {
                        this.config_to_change = null; // Clear the name of the configuration being modified
                        this.new_config = false; // Reset the flag indicating if a new configuration is being created
                        this.name_entity = null; // Clear the name of the entity
                        this.question = null; // Clear the current question
                        this.name_new_config = null; // Clear the name of the new configuration being created
                        this.model_choosen = null; // Clear the name of the model used for question answering
                        this.high_text = null;
                        this.saving_question = false;
                        this.showSave = true;

                        setTimeout(() => {
                            this.showSave = false;
                        }, 2000);

                        // Retrieve the updated configuration
                        axios.post("http://localhost:8000/api/load-config/", {
                            file_txt_path: this.txt_file,
                            language: this.language,
                            text: this.text,
                            f_up: this.file_uploaded // The uploaded file, if any
                        })
                            .then(response => {
                                this.dictionaryObj = JSON.parse(response.data.jsonner_str); // Parse the configuration as a JSON object
                                this.file_config = response.data.jsonNER; // Store the configuration file
                                this.loaded = true; // Set the loaded flag to true
                                this.model_entity = JSON.parse(response.data.entity_model_current); // Parse the model entity as a JSON object
                                this.str_dict = response.data.jsondict_str;
                            })
                            .catch(error => {
                                console.log(error); // Log any errors to the console
                                alert(error); // Display an alert with the error message

                                this.saving_question = false;
                            });
                        // Retrieve the available configurations
                        axios.post("http://localhost:8000/api/get-config/", { "language": this.language })
                            .then(response => {
                                if (this.language == "it") {
                                    this.available_configs_it = response.data.configs; // Store the Italian configurations
                                }
                                else {
                                    this.available_configs_en = response.data.configs; // Store the English configurations
                                }
                            }).catch(error => {
                                console.log(error); // Log any errors to the console
                                alert(error); // Display an alert with the error message

                                this.saving_question = false;
                            });
                        setTimeout(() => {
                            window.scrollTo(0, document.body.scrollHeight);
                        }, 500);
                    }

                })
                .catch(error => {
                    console.log(error); // Log any errors to the console
                    alert(error); // Display an alert with the error message

                    this.saving_question = false;
                });


        },
        // This function changes the configuration settings and loads the updated configuration file.
        changeConfig() {
            this.loading_change = true;
            this.scrollDown();
            // Send a POST request to the API endpoint to change the configuration settings.
            axios.post("http://localhost:8000/api/change-cnf/", { config_name: this.config_to_change, txt: this.txt_file, language: this.language, context: this.text })
                .then(response => {
                    // If the response from the API contains an error code, display an alert with the error message.
                    this.code = response.data.cod;
                    if (this.code == -1) {
                        alert(response.data.res);
                        this.loading_change = false;
                    }
                    // If there is no error, load the updated configuration file and update the available configuration options.
                    else {
                        // Clear the current configuration selection.
                        this.config_to_change = null;
                        // Send a POST request to the API endpoint to load the updated configuration file.
                        axios.post("http://localhost:8000/api/load-config/", { file_txt_path: this.txt_file, language: this.language, text: this.text, f_up: this.file_uploaded })
                            .then(response => {
                                // Parse the loaded JSON data into an object and set it to a variable.
                                this.dictionaryObj = JSON.parse(response.data.jsonner_str);
                                // Set the loaded configuration file to a variable.
                                this.file_config = response.data.jsonNER;
                                // Set the loaded flag to true to indicate that the configuration has been loaded.
                                this.loaded = true;
                                // Parse the current entity model into an object and set it to a variable.
                                this.model_entity = JSON.parse(response.data.entity_model_current);
                                // JSON string of the dictionary
                                this.str_dict = response.data.jsondict_str;
                            })
                            .catch(error => {
                                // Display an alert with the error message if the configuration file fails to load.
                                console.log(error);
                                alert(error);
                                this.loading_change = false;
                            });
                        // Send a POST request to the API endpoint to get the available configuration options.
                        axios.post("http://localhost:8000/api/get-config/", { "language": this.language })
                            .then(response => {
                                // If the language is Italian, update the available Italian configuration options.
                                if (this.language == "it") {
                                    this.available_configs_it = response.data.configs;
                                }
                                // If the language is English, update the available English configuration options.
                                else {
                                    this.available_configs_en = response.data.configs;
                                }
                            }).catch(error => {
                                // Display an alert with the error message if the configuration options fail to load.
                                console.log(error);
                                alert(error);
                                this.loading_change = false;
                            });
                        this.loading_change = false;
                        this.showChange = true;

                        setTimeout(() => {
                            this.showChange = false;
                        }, 2000);
                    }
                    setTimeout(() => {
                        window.scrollTo(0, document.body.scrollHeight);
                    }, 500);
                })
                .catch(error => {
                    // Display an alert with the error message if there is an error with the POST request.
                    console.log(error);
                    alert(error);
                    this.loading_change = false;

                    // Clear the current configuration selection.

                    this.config_to_change = null;

                    // Send a POST request to the API endpoint to load the updated configuration file.

                    axios.post("http://localhost:8000/api/load-config/", { file_txt_path: this.txt_file, language: this.language, text: this.text, f_up: this.file_uploaded })
                        .then(response => {
                            // Parse the loaded JSON data into an object and set it to a variable.
                            this.dictionaryObj = JSON.parse(response.data.jsonner_str);
                            // Set the loaded configuration file to a variable.
                            this.file_config = response.data.jsonNER;
                            // Set the loaded flag to true to indicate that the configuration has been loaded.
                            this.loaded = true;
                            // Parse the current entity model into an object and set it to a variable.
                            this.model_entity = JSON.parse(response.data.entity_model_current);
                            // JSON string of the dictionary
                            this.str_dict = response.data.jsondict_str;
                        })
                        .catch(error => {
                            // Display an alert with the error message if the configuration file fails to load.
                            console.log(error);
                            alert(error);
                            this.loading_change = false;
                        });
                });


        },
        // This function deletes entities from the configuration file.
        deleteEn() {
            // Send a POST request to the API endpoint to delete the specified entities.
            axios.post("http://localhost:8000/api/delete-entities/", { "file_config": this.file_config, "entities": this.todelete_entities })
                .then(response => {
                    // If the response from the API contains an error code, display an alert with the error message.
                    if (response.data.cod == -1) {
                        alert(response.data.res);
                    }
                    // If there is no error, reload the configuration file and update the available configuration options.
                    else {
                        // Clear the current list of entities to delete.
                        this.todelete_entities = [];
                        this.selectedEntities = [];
                        this.colors = [];
                        this.high_text = null;
                        this.showDelete = true;

                        setTimeout(() => {
                            this.showDelete = false;
                        }, 2000);

                        this.scrollDown();
                        // Send a POST request to the API endpoint to load the updated configuration file.
                        axios.post("http://localhost:8000/api/load-config/", { file_txt_path: this.txt_file, language: this.language, text: this.text, f_up: this.file_uploaded })
                            .then(response => {
                                // Parse the loaded JSON data into an object and set it to a variable.
                                this.dictionaryObj = JSON.parse(response.data.jsonner_str);
                                // Set the loaded configuration file to a variable.
                                this.file_config = response.data.jsonNER;
                                // Set the loaded flag to true to indicate that the configuration has been loaded.
                                this.loaded = true;
                                // Parse the current entity model into an object and set it to a variable.
                                this.model_entity = JSON.parse(response.data.entity_model_current);
                                // JSON string of the dictionary
                                this.str_dict = response.data.jsondict_str;

                            })
                            .catch(error => {
                                // Display an alert with the error message if the configuration file fails to load.
                                console.log(error);
                                alert(error);
                            });
                        // Send a POST request to the API endpoint to get the available configuration options.
                        axios.post("http://localhost:8000/api/get-config/", { "language": this.language })
                            .then(response => {
                                // If the language is Italian, update the available Italian configuration options.
                                if (this.language == "it") {
                                    this.available_configs_it = response.data.configs;
                                }
                                // If the language is English, update the available English configuration options.
                                else {
                                    this.available_configs_en = response.data.configs;
                                }
                            }).catch(error => {
                                // Display an alert with the error message if the configuration options fail to load.
                                console.log(error);
                                alert(error);
                            });
                    }
                }).catch(error => {
                    // Display an alert with the error message if there is an error with the POST request.
                    console.log(error);
                    alert(error);
                });




        },
        // This function download the json file
        downloadJson() {
            // Create a new Blob object with the JSON data string and set the MIME type to application/json
            const blob = new Blob([this.str_dict], { type: "application/json" });
            // Create a URL for the Blob object
            const url = URL.createObjectURL(blob);
            // Create a new anchor element
            const link = document.createElement("a");
            // Set the download attribute to the desired file name (in this case, data.json)
            link.setAttribute("download", "data.json");
            // Set the href attribute to the URL of the Blob object
            link.setAttribute("href", url);
            // Append the anchor element to the document body
            document.body.appendChild(link);
            // Simulate a click on the anchor element to start the download
            link.click();
            // Remove the anchor element from the document body
            document.body.removeChild(link);
        },
        // This function scroll the page until the bottom
        scrollDown() {
            setTimeout(() => {
                window.scrollTo(0, document.body.scrollHeight);
            }, 500);
        }
    },

    mounted() {

        this.dictionaryObj = null;
        this.upload = true;

        $(window).scroll(function () {
            if ($(this).scrollTop() < 0) {
                $('.back-to-top').fadeOut();
            } else {
                $('.back-to-top').fadeIn();
            }
        });

        $(window).scroll(function () {
            if ($(this).scrollTop() == $(document).height()) {
                $('.back-to-bottom').fadeOut();
            } else {
                $('.back-to-bottom').fadeIn();
            }
        });

        $('.back-to-top').click(function () {
            $('html, body').animate({ scrollTop: 0 }, 500);
            return false;
        });

        $('.back-to-bottom').click(function () {
            $('html, body').animate({ scrollTop: $(document).height() }, 500);
            return false;
        });
    }

};
</script>

<style>
.toast {
    bottom: 20px;
    left: 20px;
}

.back-to-top {
    position: fixed;
    bottom: 20px;
    right: 20px;
    display: none;
}

.back-to-bottom {
    position: fixed;
    bottom: 80px;
    right: 20px;
    display: none;
}

.legend {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
}

.legend-title {
    margin-right: 0.5rem;
}

.legend-item {
    display: flex;
    align-items: center;
    margin-right: 1rem;
    margin-bottom: 0.5rem;
}

.color-box {
    width: 50px;
    height: 50px;
    margin-right: 5px;
    border: 10px black;
}

.entity-name {
    font-size: 15px;
}

.container {
    display: flex;
    flex-direction: row;
}

.table {
    flex-grow: 1;
    margin-right: 10px;
}
</style>
