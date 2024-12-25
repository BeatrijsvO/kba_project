<?php
/*
Plugin Name: KBA Agent FastAPI Document Manager
Description: Plugin om documenten te beheren via een FastAPI-backend.
Version: 1.0
Author: YininIT
*/

function document_manager_shortcode() {
    return '
    <form id="upload-form">
        <label for="files">Upload Documenten:</label>
        <input type="file" id="files" name="files" multiple>
        <button type="button" onclick="uploadDocuments()">Upload</button>
    </form>
    <form id="delete-form">
        <label for="filename">Verwijder Document:</label>
        <input type="text" id="filename" name="filename">
        <button type="button" onclick="deleteDocument()">Verwijder</button>
    </form>
    <div id="document-list">
        <h3>Documenten:</h3>
        <ul id="documents"></ul>
    </div>
    <script src="' . plugins_url('script.js', __FILE__) . '"></script>
    ';
}

add_shortcode('document_manager', 'document_manager_shortcode');
?>