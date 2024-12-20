<?php
/*
Plugin Name: KBA Plugin
Description: Verbind met KBA API.
Version: 1.0
Author: Jouw Naam
*/

function kba_enqueue_scripts() {
    // Registreer en laad het JavaScript-bestand
    wp_enqueue_script(
        'kba-api-script', // Unieke naam
        plugins_url('js/kba-api.js', __FILE__), // Pad naar het bestand
        array('jquery'), // Vereisten (optioneel)
        null, // Versie (null = geen cache)
        true // Plaats in de footer
    );
}
add_action('wp_enqueue_scripts', 'kba_enqueue_scripts');


function kba_shortcode_form() {
    ob_start();
    ?>
    <form id="kbaForm">
        <label for="kbaVraag">Stel je vraag:</label>
        <input type="text" id="kbaVraag" name="vraag" required>
        <button type="submit">Verstuur</button>
    </form>
    <div id="kbaResult"></div>
    <?php
    return ob_get_clean();
}
add_shortcode('kba_form', 'kba_shortcode_form');

